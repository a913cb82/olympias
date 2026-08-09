#!/usr/bin/env python3
"""Extract posts from archived Model Ship World topic 21958 pages (IPB HTML)."""
import re, html as htmllib, sys

def unescape(s):
    return htmllib.unescape(s)

def extract_articles(html_str):
    articles = []
    pattern = re.compile(r"<article\s+id=['\"]elComment_(\d+)['\"].*?</article>", re.S)
    for m in pattern.finditer(html_str):
        articles.append((m.group(1), m.group(0)))
    return articles

def get_author(seg):
    m = re.search(r"cAuthorPane_author.*?ipsType_break['\"][^>]*>(?:<span[^>]*>)?([^<]+?)(?:</span>)?</a>", seg, re.S)
    if not m:
        m = re.search(r"cAuthorPane_author.*?>(?:<strong>)?<a[^>]*>([^<]+)</a>", seg, re.S)
    return unescape(m.group(1)).strip() if m else None

def get_postnum(seg):
    m = re.search(r">#(\d+)</a>", seg)
    return int(m.group(1)) if m else None

def get_date(seg):
    m = re.search(r"<time datetime='(\d{4}-\d{2}-\d{2}T[\d:]+Z)'", seg)
    return m.group(1) if m else None

def get_edited(seg):
    m = re.search(r"Edited\s*<time datetime='([^']+)'[^>]*>(.*?)</time>\s*by\s*([^<]+)", seg, re.S)
    if m:
        return (m.group(1), unescape(m.group(3)).strip())
    return None

def extract_balanced_div(seg, attr='data-role="commentContent"'):
    """Find the div starting with attr and return its inner HTML, balancing nested divs."""
    start = seg.find(attr)
    if start == -1:
        return ""
    # move to '<' of the opening tag
    tag_start = seg.rfind('<', 0, start)
    # find end of opening tag
    gt = seg.find('>', start)
    if gt == -1:
        return ""
    depth = 1
    i = gt + 1
    # scan for nested div open/close
    while i < len(seg):
        lt = seg.find('<', i)
        if lt == -1:
            break
        # check if this is a comment or closing
        if seg[lt:lt+4] == '<!--':
            ce = seg.find('-->', lt)
            i = ce + 3 if ce != -1 else lt + 4
            continue
        gt = seg.find('>', lt)
        if gt == -1:
            break
        tag = seg[lt+1:gt].strip()
        if tag.startswith('div'):
            depth += 1
        elif tag.startswith('/div'):
            depth -= 1
            if depth == 0:
                return seg[tag_start + (seg.find('>', tag_start) - tag_start) + 1 : lt]
        elif tag.startswith('!'):
            pass
        i = gt + 1
    return ""

def extract_body(seg):
    inner = extract_balanced_div(seg)
    # remove the edited span inside
    inner = re.sub(r'<span class=[\'"]ipsType_reset ipsType_medium ipsType_light[\'"][^>]*>.*?</span>', '', inner, flags=re.S)
    return inner.strip()

def strip_quote_blocks(body):
    """Replace [quote] blocks with a quoted notation, preserving original text."""
    def repl(m):
        quote = m.group(0)
        inner = re.sub(r'</?blockquote[^>]*>', '', quote)
        inner = re.sub(r'<cite[^>]*>.*?</cite>', '', inner, flags=re.S)
        # convert inner HTML to plain text roughly
        inner = re.sub(r'</(p|div)>', '\n', inner)
        inner = re.sub(r'<br\s*/?>', '\n', inner)
        inner = re.sub(r'<[^>]+>', '', inner)
        inner = htmllib.unescape(inner)
        inner = re.sub(r'[ \t]+\n', '\n', inner)
        inner = re.sub(r'\n{2,}', '\n', inner)
        inner = inner.strip()
        # attribute line "On ... said:" becomes a prefix line
        att = re.search(r'^On .+ said:', inner)
        prefix = att.group(0) if att else ''
        if att:
            inner = inner[len(prefix):].strip()
        q = '\n'.join(f'> {l}' for l in inner.split('\n'))
        return (f'\n{prefix}\n\n{q}\n' if prefix else f'\n{q}\n')
    body = re.sub(r'<blockquote[^>]*>.*?</blockquote>', repl, body, flags=re.S)
    return body

def extract_images(body):
    images = []
    def img_repl(m):
        src = m.group(1)
        alt = (m.group(2) or 'photo')
        images.append((src, alt))
        return f"@@IMG{len(images)-1}@@"
    def img_repl_rev(m):
        alt = m.group(1)
        src = m.group(2)
        images.append((src, alt))
        return f"@@IMG{len(images)-1}@@"
    # First, handle full attach-link wrappers: <a class="ipsAttachLink..." href="FULL">...<img src="THUMB">...</a>
    def attach_repl(m):
        full = m.group(1)
        inner = m.group(2)
        sm = re.search(r'<img[^>]*>', inner)
        alt = 'photo'
        if sm:
            am = re.search(r'alt=[\'"]([^\'"]*)[\'"]', sm.group(0))
            alt = am.group(1) if am else 'photo'
        images.append((full, alt))
        return f"@@IMG{len(images)-1}@@"
    body = re.sub(r'<a\s+class=["\']ipsAttachLink[^"\']*["\'][^>]*?\shref=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>', attach_repl, body, flags=re.S)
    body = re.sub(r'<img[^>]*src=[\'"]([^\'"]+)[\'"][^>]*alt=[\'"]([^\'"]*)[\'"][^>]*/?>', img_repl, body)
    body = re.sub(r'<img[^>]*alt=[\'"]([^\'"]*)[\'"][^>]*src=[\'"]([^\'"]+)[\'"][^>]*/?>', img_repl_rev, body)
    body = re.sub(r'<img[^>]*src=[\'"]([^\'"]+)[\'"][^>]*/?>', img_repl, body)
    return body, images

def body_to_markdown(body):
    body = strip_quote_blocks(body)
    body, images = extract_images(body)
    # remove reaction/attachment wrappers
    body = re.sub(r'<a class="ipsAttachLink[^>]*>', '', body)
    body = re.sub(r'</a>', '', body)
    # block elements -> newlines
    body = re.sub(r'</(p|div|ul|ol)>', '\n', body)
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'<(li|h[1-6])[^>]*>', '* ', body)
    body = re.sub(r'<(ul|ol)[^>]*>', '', body)
    body = re.sub(r'<[^>]+>', '', body)
    body = unescape(body)
    body = re.sub(r'[ \t]+\n', '\n', body)
    body = re.sub(r'\n{3,}', '\n\n', body)
    lines = body.split('\n')
    result = []
    for line in lines:
        s = line.strip()
        while True:
            mm = re.search(r'@@IMG(\d+)@@', s)
            if not mm:
                break
            idx = int(mm.group(1))
            src, alt = images[idx]
            result.append(f"![{alt}]({src})")
            s = s.replace(mm.group(0), '', 1)
        if s.strip():
            result.append(s)
    return '\n'.join(result)

def parse_file(path):
    raw = open(path, encoding='utf-8').read()
    posts = []
    for cid, seg in extract_articles(raw):
        posts.append({
            'commentid': cid,
            'postnum': get_postnum(seg),
            'author': get_author(seg),
            'date': get_date(seg),
            'edited': get_edited(seg),
            'body': body_to_markdown(extract_body(seg)),
        })
    return posts

if __name__ == '__main__':
    for p in sys.argv[1:]:
        posts = parse_file(p)
        print(f"== {p}: {len(posts)} posts ==")
        for post in posts:
            a = post['author']
            mark = "RICHARD" if (a and 'Braithwaite' in a) else "other  "
            print(f"  {mark}  post#{post['postnum']} comment={post['commentid']} date={post['date']} edited={bool(post['edited'])} bodylen={len(post['body'])}")
