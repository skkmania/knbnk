import cv2

img = cv2.imread('data/001.jpeg')
cv2.imwrite('data/001_out_no_spec.jpeg', img)

img = cv2.imread('data/001.jpeg', cv2.CV_LOAD_IMAGE_COLOR)
cv2.imwrite('data/001_out_color.jpeg', img)

img = cv2.imread('data/001.jpeg', cv2.CV_LOAD_IMAGE_GRAYSCALE)
cv2.imwrite('data/001_out_gray.jpeg', img)

img = cv2.imread('data/001.jpeg', cv2.CV_LOAD_IMAGE_UNCHANGED)
cv2.imwrite('data/001_out_unchanged.jpeg', img)

