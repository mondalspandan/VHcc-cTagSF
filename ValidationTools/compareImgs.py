from PIL import Image, ImageDraw, ImageFont
import os,sys
s=600

indir = sys.argv[1]


dirlist = [os.path.join(indir,i) for i in os.listdir(indir) if os.path.isdir(os.path.join(indir,i)) and "central" in i]

for i in dirlist:
    if i.endswith("central"):
        centraldir = i
        dirlist.remove(i)
        break
subdirs = sorted([i for i in dirlist if "semilep" in i])
subdirs += sorted([i for i in dirlist if "dilep" in i])
subdirs += sorted([i for i in dirlist if "inclTTbar" in i])
subdirs += sorted([i for i in dirlist if "combined" in i])

pnglist = [i for i in os.listdir(centraldir) if i.endswith(".png")]

def getName(fl):
    if 'is_E_' in fl and 'nJet_0-4' in fl:
        return "W+c (e)"
    elif 'is_M_' in fl and 'nJet_0-4' in fl:
        return u"W+c (\u03BC)"
    elif 'is_E_' in fl and 'nJet_5-' in fl:
        return "TTSemileptonic (e)"
    elif 'is_M_' in fl and 'nJet_5-' in fl:
        return u"TTSemileptonic (\u03BC)"
    elif 'is_ME_' in fl:
        return u"TTDileptonic (\u03BCe)"
    elif 'is_MM_' in fl:
        return u"TTDileptonic (\u03BC\u03BC)"
    elif 'is_EE_' in fl:
        return "TTDileptonic (ee)"
    else:
        return "DY + light"

for fl in sorted(pnglist):
#    if not fl.startswith("jet_Cvs"): continue
    out = Image.new("RGB", (s*5,(s+s/6)*2),(255, 255, 255))
    draw = ImageDraw.Draw(out)
    font_size = int(s/15)
    font = ImageFont.truetype('/usr/share/fonts/dejavu/DejaVuSans.ttf', font_size)
    font2 = ImageFont.truetype('/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf', font_size)
    img1 = Image.open(os.path.join(centraldir,fl))
    img1=img1.resize((s,s), Image.ANTIALIAS)
    out.paste(img1,(0,s/2+s/3))
    
    flname = getName(fl)
    w, h = draw.textsize(flname,font=font2)        
    draw.text((s/2-w/2,s/2+s/3-h-s/4), flname,font=font2,fill='rgb(0, 0, 0)')
    
    w, h = draw.textsize("No SF applied",font=font)        
    draw.text((s/2-w/2,s/2+s/3-h-s/40), "No SF applied",font=font,fill='rgb(0, 0, 0)')
    skip=False
    x=s
    y=s/6
    for idir,subdir in enumerate(subdirs):
        categoryname = subdir.split("/")[-1].split('_')[-1]
        if not os.path.isfile(os.path.join(subdir,fl)):
            skip=True
            continue        
        img2 = Image.open(os.path.join(subdir,fl))
        img2=img2.resize((s,s), Image.ANTIALIAS)
        out.paste(img2,(x,y))
        w, h = draw.textsize(categoryname,font=font)        
        draw.text((x+s/2-w/2,y-h-s/40), categoryname,font=font,fill='rgb(0, 0, 0)')
        if idir==3:
            y+=s+s/6
            x=s
        else:
            x+=s
    if skip: continue
    print "Exporting",fl
    outDirname=fl.split('+')[0].split('_')[0]+"_"+fl.split('+')[0].split('_')[1]
    os.system("mkdir -p "+indir+"/SFcompare/"+outDirname)
    out.save(os.path.join(indir,"SFcompare",outDirname,fl))
