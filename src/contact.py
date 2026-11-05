from PIL import Image, ImageDraw, ImageFont
import glob, os
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
F=ImageFont.truetype("/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf",26); F.set_variation_by_name("Bold")
G=ImageFont.truetype("/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf",34); G.set_variation_by_name("Bold")
def grid(fmt,cols,tw):
    fs=sorted(glob.glob(f'{R}/{fmt}/*.png')); ims=[Image.open(f).convert('RGB') for f in fs]
    th=round(tw*ims[0].height/ims[0].width); rows=(len(ims)+cols-1)//cols
    g=Image.new('RGB',(cols*(tw+12)+12,rows*(th+12)+12),(236,231,214)); d=ImageDraw.Draw(g)
    for i,im in enumerate(ims):
        x,y=12+(i%cols)*(tw+12),12+(i//cols)*(th+12)
        g.paste(im.resize((tw,th),Image.LANCZOS),(x,y))
        d.rounded_rectangle((x+6,y+6,x+6+44 if i<9 else x+6+54,y+40),radius=6,fill=(78,107,34)); d.text((x+12,y+8),str(i+1),font=F,fill=(246,241,227))
    return g
w=grid('wide',5,500); v=grid('vert',10,250)
W=max(w.width,v.width); H=w.height+v.height+170
c=Image.new('RGB',(W,H),(236,231,214)); d=ImageDraw.Draw(c)
d.text((14,14),"Galatians 6 live slides: WIDE 1920x1080 (35)",font=G,fill=(78,107,34)); c.paste(w,(0,60))
y=60+w.height+30; d.text((14,y),"VERTICAL 1080x1920 (35), same numbering",font=G,fill=(78,107,34)); c.paste(v,(0,y+50))
c.save(f'{R}/contact.png'); print(c.size)
