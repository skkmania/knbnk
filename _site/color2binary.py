'''
Aim:
1. Read a color image, convert it to grayscale and then use a thresholding
 filter to produce a binary image.
  2. Display the change produced by the two stages in different windows.
   3. Save the grayscale and binary images.
    
     Usage:
      color2Binary.py needs a single argument: imageName
       
        Give the name of a color image file and include its path if the image file is
         not in the same location as color2Binary.py
          
           Command line use:
            python color2Binary.py /pathToFile/colorPic.jpg
             
              See cv2.nameWindow, cv2.imshow, cv2.imread, cv2.moveWindow, cv2.cvtColor and
               cv2.threshold in "OpenCV2 Reference Manual" for more information.
                
                 Author: Sameer Khan (samkhan13.wordpress.com)
                  July 30th 2012
                   No copyrights, warranty or guaranties of any kind are associated with this file.
                   '''
                    
                    ## use sys, cv2 and numpy packages
                    import sys, cv2
                    import numpy as np
                     
                     ## main function
                      def startExercise(imageName):
                         ## read source image and get its shape
                          sourceImage = cv2.imread(imageName, -1) # -1 is used to read the image as is
                           imgRows, imgCols, imgChannels = np.shape(sourceImage)
                            
                             ## color to gray scale
                              grayImage = cv2.cvtColor(sourceImage, cv2.COLOR_RGB2GRAY) # cv2.COLOR_RGB2GRAY = 7
                               grayImgName = 'gray_' + imageName
                                
                                 ## gray to binary: threshold = 100 (arbitrary); maxValue = 255; type = cv2.THRESH_BINARY
                                  flag, binaryImage = cv2.threshold(grayImage, 100, 255, cv2.THRESH_BINARY) # cv2.THRESH_BINARY = 0
                                   binaryImgName = 'binary_' + imageName
                                    
                                     ## display images in seprate windows and arrange the windows
                                      cv2.namedWindow('Color Image')
                                       cv2.moveWindow('Color Image', 0, 0) # position window at 0,0
                                        cv2.imshow('Color Image',sourceImage)
                                         
                                          cv2.namedWindow('Gray Scale Image')
                                           cv2.moveWindow('Gray Scale Image', imgCols, 0) # move window to the right
                                            cv2.imshow('Gray Scale Image',grayImage)
                                             
                                              cv2.namedWindow('Binary Image')
                                               cv2.moveWindow('Binary Image', 2*imgCols, 0) # move window further to the right
                                                cv2.imshow('Binary Image',binaryImage)
                                                 
                                                  ## wait for user input
                                                   keyPress = cv2.waitKey(0) # 0 means wait indefinitely
                                                    
                                                     if keyPress == ord('s'): # save images and quit
                                                         cv2.imwrite(grayImgName, grayImage)
                                                           cv2.imwrite(binaryImgName, binaryImage)
                                                            
                                                              print "\nImages were saved in the working directory.\nPress any key to quit.\n"
                                                               
                                                                 cv2.waitKey(0)
                                                                   cv2.destroyAllWindows()
                                                                    
                                                                     elif keyPress == ord('q'): # quit without saving images
                                                                         cv2.destroyAllWindows()
                                                                          
                                                                           
                                                                           ## for using color2Binary.py from the command line
                                                                           if __name__ == '__main__':
                                                                            if len(sys.argv)!=2:
                                                                                print __doc__
                                                                                 else:
                                                                                   print "\nInstructions:\n\tClick on the display windows to bring them into focus.\n"
                                                                                     print "Options:\n\tPress s to save images.\n\tPress q to quit without saving.\n"
                                                                                      
                                                                                        imageName = sys.argv[1]
                                                                                          startExercise(imageName)
                                                                                           
                                                                                           ## end of color2Binary.py
