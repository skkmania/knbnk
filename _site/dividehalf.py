import os,sys
import PIL.Image as Image
import os.path

infilename = sys.argv[1]
name, ext = os.path.splitext(infilename)
outfilename0 = name + "_0" + ext
outfilename1 = name + "_1" + ext

im = Image.open(infilename)
width,height = im.size
box0 = (int(width/2), 0, width, height)
box1 = (0, 0, int(width/2), height)
region0 = im.crop(box0)
region1 = im.crop(box1)
region0.save(outfilename0,"JPEG")
region1.save(outfilename1,"JPEG")
