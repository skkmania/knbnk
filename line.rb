require "opencv"

#
#  if given line is :
#  vertical   => true
#  horizontal => false
#  else       => nil
#
def vert_or_horiz line
  return true  if line.point1.x == line.point2.x
  return false if line.point1.y == line.point2.y
  return nil
end

def comp_v_line line1, line2
    diff = line1.point1.x - line2.point1.x
    case
      when  diff < 0
        return :left
      when  diff == 0
        return :same_x
      when  diff > 0
        return :right
    end
end

def comp_h_line line1, line2
    diff = line1.point1.y - line2.point1.y
    case
      when  diff < 0
        return :upper
      when  diff == 0
        return :same_y
      when  diff > 0
        return :lower
    end
end
  
#Load image
cvmat = OpenCV::CvMat.load(ARGV[0])

#処理時間節約のためminimatという縮小画像をつくり4隅を計算する
scale = 0.2

newSize = OpenCV::CvSize.new
newSize.width  = cvmat.width * scale
newSize.height = cvmat.height * scale
minimat = cvmat.resize(newSize) 

# The "canny" edge-detector does only work with grayscale images
# so to be sure, convert the image
# otherwise you will get an OpenCV::CvStsAssert exception.
minimat = minimat.BGR2GRAY

# Use the "canny" edge detection algorithm (http://en.wikipedia.org/wiki/Canny_edge_detector)
# Parameters are two colors that are then used to determine possible corners
canny = minimat.canny(50, 150)

# Look for lines
lines = canny.hough_lines(OpenCV::CV_HOUGH_PROBABILISTIC,  1, 1.57, 50, 50, 32 )

v_lines, h_lines = lines.partition{|l| vert_or_horiz l }
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
