import sys
import pymupdf

import os
_BASE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(_BASE, '..', 'sources', 'rankov2012.pdf')
doc = pymupdf.open(DOC)
page = doc[244]

# decode maps: font -> {PUA: char}
# font 291 (table body) and 292 (smaller / superscripts?)
DECODES = {
    'TT291t00': {
        'F001': 'M', 'F002': 'J', 'F003': 'S', 'F005': 'O', 'F006': 'f',
        'F007': 'v', 'F008': 'c', 'F009': 'l', 'F00A': '4', 'F00B': '2',
        'F00C': '.', 'F00D': '0', 'F00E': 't', 'F00F': 'n', 'F010': 'A',
        'F011': 'p', 'F012': 'f', 'F013': 'd', 'F014': 'y', 'F015': 'm',
        'F016': 'i', 'F017': 'c', 'F018': 'w', 'F019': '6', 'F01A': '8',
        'F01B': 'D', 'F01C': '3', 'F01D': 'b', 'F01E': 'h', 'F01F': 'u',
        'F020': '7', 'F021': 'k', 'F022': '(', 'F023': ')', 'F024': '-',
        'F025': '9', 'F026': '3', 'F027': '1', 'F028': 'N', 'F029': 'E',
        'F02A': '-', 'F02B': '5', 'F02C': 'w', 'F02D': 'H', 'F02E': 'K',
        'F02F': 'C', 'F030': 'L', 'F031': 'X', 'F032': 'x', 'F033': 'C',
        'F034': 'V', 'F035': '?',
    },
    'TT292t00': {},
}

# Gather chars with positions, ordered
d = page.get_text('rawdict')
items = []
for b in d['blocks']:
    for l in b.get('lines', []):
        y = l['bbox'][1]
        for s in l['spans']:
            font = s['font']
            for ch in s['chars']:
                c = ch['c']
                x = ch['bbox'][0]
                if 0xF000 <= ord(c) <= 0xF0FF:
                    pua = hex(ord(c))[2:].upper().zfill(4)
                    items.append((y, x, font, pua, ch['bbox']))
                else:
                    items.append((y, x, font, c, ch['bbox']))

items.sort(key=lambda t: (round(t[0], 1), t[1]))

# Group into lines
lines = []
cur = []
lasty = None
for y, x, font, pua, bb in items:
    if lasty is not None and abs(y - lasty) > 1.2:
        lines.append(cur)
        cur = []
    cur.append((x, font, pua, bb))
    lasty = y
if cur:
    lines.append(cur)

for li, line in enumerate(lines):
    parts = []
    for x, font, pua, bb in line:
        if pua.startswith('F0') and font == 'TT291t00':
            ch = DECODES['TT291t00'].get(pua, '?')
        else:
            ch = pua
        parts.append((round(x, 1), ch))
    # merge adjacent same-line chars into words separated by gaps > 5pt
    words = []
    for x, ch in parts:
        if words and x - words[-1][0] > 6:
            words.append((x, ' | '))
        words.append((x, ch))
    print(f"R{li:02d}: " + "".join(ch for _, ch in words))
