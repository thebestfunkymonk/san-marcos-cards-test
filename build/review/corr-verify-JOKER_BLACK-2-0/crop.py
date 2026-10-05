import subprocess, sys, re, os
def crop(svg, x0,y0,x1,y1, scale, out):
    s=open(svg).read()
    w=(x1-x0)*scale; h=(y1-y0)*scale
    s=re.sub(r'<svg[^>]*>', f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="{x0} {y0} {x1-x0} {y1-y0}">', s, count=1)
    tmp=out+'.svg'; open(tmp,'w').write(s)
    subprocess.run(['rsvg-convert','-o',out,tmp],check=True); os.remove(tmp)
if __name__=='__main__':
    svg,x0,y0,x1,y1,s,out=sys.argv[1:]
    crop(svg,float(x0),float(y0),float(x1),float(y1),float(s),out)
