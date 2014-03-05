import sys
import numpy as np
import cv2
from operator import itemgetter, attrgetter


def comp_h_line(line1, line2)
    diff = line1.point1.y - line2.point1.y
    if    diff <  0: return "upper"
    elif  diff == 0: return "same_y"
    elif  diff >  0: return "lower"

def comp_v_line(line1, line2)
    diff = line1.point1.x - line2.point1.x
    if    diff <  0: return "left"
    elif  diff == 0: return "same_x"
    elif  diff >  0: return "right"

#
#  if given line is :
#  vertical   => true
#  horizontal => false
#  else       => nil
#
def vert_or_horiz(line):
  if line.point1.x == line.point2.x:
    return true
  if line.point1.y == line.point2.y:
    return false 
  return nil

def separate(arr, x):
  if x[1] - arr[-1][-1][1] < 15:
    arr[-1].append(x)
  else:
    arr.append([x])
  return arr
 
infilename = sys.argv[1]
outfilename = 'conts_' + infilename
centsfilename = 'cents_' + infilename
maskfilename = 'mask_' + infilename
meanfilename = 'mean_' + infilename

#Load image
im = cv2.imread(infilename)
height, width, depth = im.shape

#処理時間節約のためminimatという縮小画像をつくり4隅を計算する
scale = 0.2
resize(im, minimat, Size(), scale, scale, interpolation) 
minimat = cv2.cvtColor(minimat,cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(minimat,50,255,0)
# Look for lines
lines = cv2.HoughLines(thresh, 1, 1.57, 50, 50, 32)
v_lines, h_lines = lines.partition{|l| vert_or_horiz l }

om    = np.zeros((height,width,3), np.uint8)
cents = np.zeros((height,width,3), np.uint8)
#contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
contours, hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

centroids = []

for cnt in contours:
  x,y,w,h = cv2.boundingRect(cnt)
  cv2.rectangle(om, (x, y), (x+w, y+h), [0,255,0])
  if (int(w) in range(60,120)) or (int(h) in range(60,120)):
    centroids.append((x+w/2, y+h/2))
    cv2.circle(cents, (int(x+w/2), int(y+h/2)), 5, [0,255,0])

#for h,cnt in enumerate(contours):
#  mask = np.zeros(imgray.shape,np.uint8)
#  cv2.drawContours(mask,[cnt],0,255,-1)
#  mean = cv2.mean(im,mask = mask)

centsgray = cv2.cvtColor(cents,cv2.COLOR_BGR2GRAY)

for line in lines:
  cv2.line(cents, (int(line[0][0]),int(line[0][1])), (int(line[1][0]),int(line[1][1])), 1, 255)

cv2.imwrite(outfilename, om)
cv2.imwrite(centsfilename, cents)
#cv2.imwrite(maskfilename, mask)
#cv2.imwrite(meanfilename, mean)

#for p in sorted(centroids,key=itemgetter(1,0)):
#  print str(p[0]) + ", " + str(p[1])

sorted_centroids = sorted(centroids,key=itemgetter(1,0))

grouped_centroids = reduce(separate, sorted_centroids, [sorted_centroids[0:1]])

cnt = 0
for ar in grouped_centroids:
  print "group " + str(cnt)
  for p in ar:
    print "  " + str(p[0]) + ", " + str(p[1])
  cnt = cnt + 1
 

###############################

  


cnt = 0
puts "vertical lines : #{v_lines.size}"
puts "horizontal lines : #{h_lines.size}"


right_vert     = v_lines.shift
left_vert   = right_vert

v_lines.each do |line|
    if comp_v_line(line, left_vert) == :left
        left_vert = line
        puts "left_vert : #{left_vert.point1.x},#{left_vert.point1.y} - #{left_vert.point2.x},#{left_vert.point2.y}"
    end
    if comp_v_line(line, right_vert) == :right
        right_vert = line
        puts "right_vert : #{right_vert.point1.x},#{right_vert.point1.y} - #{right_vert.point2.x},#{right_vert.point2.y}"
    end
end

puts "v_lines scanned."

bottom_horizon = h_lines.shift
top_horizon = bottom_horizon

h_lines.each do |line|
    if comp_h_line(line, top_horizon) == :upper
        top_horizon = line
        puts "top_horizon : #{top_horizon.point1.x},#{top_horizon.point1.y} - #{top_horizon.point2.x},#{top_horizon.point2.y}"
    end
    if comp_h_line(line, bottom_horizon) == :lower
        bottom_horizon = line
        puts "bottom_horizon : #{bottom_horizon.point1.x},#{bottom_horizon.point1.y} - #{bottom_horizon.point2.x},#{bottom_horizon.point2.y}"
    end
end
puts "h_lines scanned."

trim_line_top = top_horizon.point1.y
trim_line_bottom = bottom_horizon.point1.y
trim_line_left = left_vert.point1.x
trim_line_right = right_vert.point1.x

# もとの画像の大きさに4隅をあわせ、切り出す
newmat = cvmat.sub_rect(trim_line_left/scale, trim_line_top/scale,
                        (trim_line_right - trim_line_left)/scale,
                        (trim_line_bottom - trim_line_top)/scale)

lines.each do |line|
  puts "- LINE FOUND - #{cnt},  x1,y1 : #{line.point1.x},  #{line.point1.y},    x2,y2 : #{line.point2.x},  #{line.point2.y}"


  #if ((line.point1.x - line.point2.x)**2 
  #   + (line.point1.y - line.point2.y)**2) > 10000 
    # Draw that line
    minimat.line! line.point1, line.point2, :color => OpenCV::CvColor::Black
    cnt += 1
  #end
end

# And save the image
puts "\nSaving image with lines"
outfilename = ARGV[0].sub(".jpeg","_mini_out.jpeg")
minimat.save_image(outfilename)
outfilename = ARGV[0].sub(".jpeg","_out.jpeg")
newmat.save_image(outfilename)

puts "top_horizon : #{top_horizon.point1.x},#{top_horizon.point1.y} - #{top_horizon.point2.x},#{top_horizon.point2.y}"
puts "bottom_horizon : #{bottom_horizon.point1.x},#{bottom_horizon.point1.y} - #{bottom_horizon.point2.x},#{bottom_horizon.point2.y}"
puts "left_vert : #{left_vert.point1.x},#{left_vert.point1.y} - #{left_vert.point2.x},#{left_vert.point2.y}"
puts "right_vert : #{right_vert.point1.x},#{right_vert.point1.y} - #{right_vert.point2.x},#{right_vert.point2.y}"
