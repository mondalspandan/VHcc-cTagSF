import sys, os
from PIL import Image, ImageFont, ImageDraw 

indir = sys.argv[1]
os.system("mkdir -p %s/compare"%indir)
subdirs = [i for i in os.listdir(indir) if i!="compare"]
centraldir = [i for i in subdirs if i.endswith("ABC") and os.path.isdir("%s/%s"%(indir,i))]
if len(centraldir) > 1:  print "WARNING: Found multiple central directories."
centraldir = centraldir[0]

pngs = [i for i in os.listdir("%s/%s"%(indir,centraldir)) if i.endswith(".png")]

for iimg in pngs:
    pnglist = ["%s/%s/%s"%(indir,centraldir,iimg)]
    for subdir in subdirs:
        if subdir == centraldir: continue
        x = "%s/%s/%s"%(indir,subdir,iimg)
        if os.path.isfile(x):
            pnglist.append(x)
    if not os.path.isfile(x): continue
    images = [Image.open(x) for x in pnglist]
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, 60+max_height), color=(255,255,255,0))
    
    font2 = ImageFont.truetype('/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf', 70)   
    
    x_offset = 100
    for i, im in enumerate(images):
        new_im.paste(im, (x_offset,60))
        draw = ImageDraw.Draw(new_im)
        font = ImageFont.truetype('/usr/share/fonts/dejavu/DejaVuSans.ttf', 50)
        font2 = ImageFont.truetype('/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf', 50)
        if i == 0: msg = "Run ABC"
        else: msg = "Run D"
        w, h = draw.textsize(msg,font=font)
        draw.text((x_offset+im.size[0]/2-w/2, 80-h/2),msg,(0,0,0),font=font)
        x_offset += im.size[0]
        
    draw = ImageDraw.Draw(new_im)
    msg = '%s (%s)'%(iimg.split('_')[0],iimg.split('_')[1])
    w, h = draw.textsize(msg,font=font2)
    draw.text((x_offset/2-w/2, 30-h/2),msg,(0,0,0),font=font2)

    new_im.save("%s/compare/%s"%(indir,iimg))
