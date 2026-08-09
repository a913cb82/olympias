import freetype, numpy as np
tt = freetype.Face('tt292.ttf')
try:
    gar = freetype.Face(io_path if False else 'font1.cff')
    print('CFF face loaded OK')
except Exception as e:
    print('CFF load failed:', e)
    # wrap CFF into an sfnt container via fontTools? fontTools can save CFF in OTF wrapper. 
    from fontTools.cffLib import CFFFontSet
    import io
    cff = CFFFontSet()
    cff.decompile(io.BytesIO(open('font1.cff','rb').read()), None)
    from fontTools.ttLib import newTable, TTFont
    otf = TTFont()
    # build minimal OTF
    from fontTools.ttLib import TTFont, newTable
    otf = TTFont()
    # create a CFF OpenType
    otf['CFF '] = newTable('CFF ')
    otf['CFF '].cff = cff
    otf['maxp'] = newTable('maxp')
    # need head, hhea, hmtx, maxp, name, post, cmap
    from fontTools.ttLib.tables._m_a_x_p import table__m_a_x_p
    from fontTools.ttLib.tables._h_h_e_a import table__h_h_e_a
    from fontTools.ttLib.tables._h_m_t_x import table__h_m_t_x
    from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e
    from fontTools.ttLib.tables._p_o_s_t import table__p_o_s_t
    from fontTools.ttLib.tables._h_e_a_d import table__h_e_a_d
    from fontTools.ttLib.tables._c_m_a_p import table__c_m_a_p
    mp = table__m_a_p.x()
    hh = table__h_h_e_a()
    hm = table__h_m_t_x()
    nm = table__n_a_m_e()
    po = table__p_o_s_t()
    hd = table__h_e_a_d()
    cm = table__c_m_a_p()
    otf['maxp'] = mp; otf['hhea']=hh; otf['hmtx']=hm; otf['name']=nm; otf['post']=po; otf['head']=hd; otf['cmap']=cm
    otf['head'].unitsPerEm = 1000
    otf['maxp'].numGlyphs = len(cff['ZDIKFF+AGaramondPro-Regular'].charset)
    otf['hhea'].ascent=800; otf['hhea'].descent=-200
    gs = cff['ZDIKFF+AGaramondPro-Regular'].getGlyphSet()
    otf['hmtx'].metrics = {n:(1000,500) for n in otf['maxp']._aslice(otf['maxp'].numGlyphs) if False}
    otf.save('gar.otf')
    gar = freetype.Face('gar.otf')
    print('OTF saved & loaded')
