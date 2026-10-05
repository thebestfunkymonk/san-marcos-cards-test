import sys, os, re, shutil; sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck/build/review/specA')
from harness import *
from inkkit import geom as G, svg as S
from deck import tokens as T
PL=os.path.join(SB,'planted'); os.makedirs(PL,exist_ok=True)
base=build('QD'); basew=build('QD','white')
src=open(base['svg']).read(); srcw=open(basew['svg']).read()
def inject(txt, layer, frag):
    key=f'<g id="{layer}" clip-path="url(#card)">'
    assert key in txt
    return txt.replace(key, key+'\n'+frag, 1)
def run(name, frags, keys):
    a=dict(base); w=dict(basew)
    t=src; tw=srcw
    for layer, frag in frags:
        t=inject(t,layer,frag); tw=inject(tw,layer,frag)
    a['svg']=os.path.join(PL,name+'.svg'); w['svg']=os.path.join(PL,name+'.white.svg'); a['stem']=name; w['stem']=name
    open(a['svg'],'w').write(t); open(w['svg'],'w').write(tw)
    r=check(a,w)
    print(f'{name:34}', row(r, keys), '|', {k:(r.get(k) or {}).get('detail',[])[:2] for k in keys if (r.get(k) or {}).get('ok') in (False,'warn')})
    return r
ln=lambda y,x0=300,x1=400: G.poly_d([(x0,y),(x1,y)])
# T1 parallel lines as STROKES 5.1 c-c (paper 3.0)  -> should FAIL (4.2)
run('T1a_parallel_strokes_gold', [('gold', S.path(ln(300)+ln(305.1), fill='none', stroke=T.FOIL, stroke_width=T.FINE))], ['12'])
# T1b same lines emitted as outlined FILLS (G.outline) -> should also FAIL
run('T1b_parallel_outlined_fills', [('gold', S.path(G.outline(ln(300),T.FINE)+G.outline(ln(305.1),T.FINE), fill=T.FOIL))], ['12'])
# T1c gold outlined fill beside ink stroke, paper 3.5
run('T1c_fill_vs_stroke_xlayer', [('gold', S.path(G.outline(ln(300),T.FINE), fill=T.FOIL)), ('ink', S.path(ln(305.1+0.5+0.5), fill='none', stroke=T.INK, stroke_width=T.FINE))], ['12'])
# T1d two FINE hatch strokes at 5.0 pitch (paper 2.9) in one path element
run('T1d_hatch_pitch5_onepath', [('gold', S.path(''.join(ln(300+5*k,300,360) for k in range(6)), fill='none', stroke=T.FOIL, stroke_width=T.FINE, stroke_linecap='butt'))], ['12'])
# T3 asymmetric (top half only) FINE gold line 100 px
run('T3a_asym_FINE_line', [('gold', S.path(ln(300), fill='none', stroke=T.FOIL, stroke_width=T.FINE))], ['10a'])
run('T3b_asym_HAIRLINE_line', [('gold', S.path(ln(300), fill='none', stroke=T.FOIL, stroke_width=T.HAIRLINE))], ['10a'])
run('T3c_asym_MEDIUM_line', [('ink', S.path(ln(300), fill='none', stroke=T.INK, stroke_width=T.MEDIUM))], ['10a'])
# T4 asymmetric dots
run('T4a_asym_dot_4.2', [('gold', S.path(G.circle_d(300,300,2.1), fill=T.FOIL))], ['10a'])
run('T4b_asym_dot_6.3', [('gold', S.path(G.circle_d(300,300,3.15), fill=T.FOIL))], ['10a'])
run('T4c_asym_dot_8.4_ink', [('ink', S.path(G.circle_d(300,300,4.2), fill=T.INK))], ['10a'])
# T5 illegal things
run('T5a_scale_in_css', [('gold', f'<g style="transform: scale(1.5)">{S.path(ln(300), fill="none", stroke=T.FOIL, stroke_width=T.FINE)}</g>')], ['1'])
run('T5b_opacity_pct', [('gold', f'<g opacity="50%">{S.path(ln(300), fill="none", stroke=T.FOIL, stroke_width=T.FINE)}</g>')], ['4'])
run('T5c_paper_halo', [('gold', S.path(ln(300), fill='none', stroke=T.PAPER, stroke_width=T.RULE))], ['4','24'])
run('T5d_fill_opacity0_cover', [('ink', S.path(G.rect_d(300,300,50,50), fill=T.INK, fill_opacity='0.0'))], ['4'])
run('T5e_stroke_no_width', [('ink', S.path(ln(300), fill='none', stroke=T.INK))], ['1'])
run('T5f_hairline_fill_0.8', [('ink', S.path(G.rect_d(300,300,60,0.8), fill=T.INK))], ['12'])
run('T5g_outside_safe', [('gold', S.path(G.circle_d(30,525,3.15), fill=T.FOIL))], ['8'])
run('T5h_gold_on_red_thin', [('red', S.path(G.rect_d(250,250,120,80), fill=T.RED)), ('gold', S.path(ln(290,260,360), fill='none', stroke=T.FOIL, stroke_width=T.FINE))], ['5r','4b'])
run('T5i_rect_clip_ignored', [('jade', '<defs><clipPath id="cx"><rect x="300" y="300" width="100" height="100"/></clipPath></defs>'+f'<g clip-path="url(#cx)">{S.path(G.rect_d(150,70,400,400), fill=T.JADE)}</g>')], ['12','4c'])

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'classes':
    pass
