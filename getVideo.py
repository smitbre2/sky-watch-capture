### Author: Brenden Smith
### File: getVideo.py
### Description: Sets up a videoObject in openCV to monitor live footage for motion
###     detection. Object detection will utilize Gaussian Blur to detect changes between frames.
import numpy as np
import cv2
import datetime
import time
import os

#This will determine sensitivity of object tracking
MIN_MOVE_AREA = 5000
PATH = os.getcwd()


def _getResolution():
    #By default the video object is passed 1080x720
    #However it will take user input of values greater than 0
    x, y, = 0, 0

    #User input must be a number >= 0; Empty input will use default values
    print("Camera resolution will need to be configured.\n",
          "Large values may be sized to hardware limitations and can have adverse affects to FPS.\n",
          "Enter blank input for default settings. (Default resolution is 1080x720).\n")
    while True:
        x = input("Enter the x resolution (Leave blank for default): ")

        if x == '':
            #default settings
            return 1080, 720

        elif int(x) > 0:
            f1 = True

            while True:
                y = input("Enter the y resolution: ")
 
                if int(y) > 0:
                    return int(x), int(y)
                    
                else:
                    print("The resolution specs must be greater than 0.")
        
        else:
            print("The resolution specs must be greater than 0.")



def _getFirstDirectory():
    #This is only called once per boot. It is a seperate function to reduce computer work.
    curr_date = datetime.date.today().strftime("%Y-%m-%d")
    dir_list = os.listdir(PATH)

    for name in dir_list:
        if curr_date == name:
            #Directory already exists
            #That means, files already exist. Check filenames for newest.
            curr_path = PATH+'\\'+curr_date    

            #Get paths to files in folder and find the newest
            file_names = os.listdir(curr_path)
            file_paths = [os.path.join(curr_path, base) for base in file_names]
            latest_file = max(file_paths, key=os.path.getctime)

            #Extract the videocount number
            index = -5
            count_string = latest_file[index]

            #Get count on previous footage. This prevents overwriting
            while True:
                index -= 1

                if latest_file[index].isdigit():
                    #Add another numerical to videocount
                    count_string += latest_file[index]

                else:
                    #Everything is done, reorder string
                    count_string = count_string[::-1]
                    count = int(count_string) + 1
                    return curr_date, count 

    #No directory, create one
    os.makedirs(curr_date)
    return curr_date, 1
    


def _getDirectory(current_date):
    #This will check for a timestamped directory in the local path.
    #If there is none, one will be made. Else it will return the current path
    new_date = datetime.date.today().strftime("%Y-%m-%d")
    if current_date == new_date:
        #No need to make a new directory
        return current_date

    #Time to make a new one
    current_date = new_date
    os.makedirs(new_date)

    #Return the timestamp of the new directory. Count will always be 1
    return new_date, 1
    


def main():
    #Providing a 0 arg grabs the first webcam. If multiple are connected,
    #The cams can be indexed further
    cap = cv2.VideoCapture(0)

    #Check resolution settings of the video object.
    #Larger values will be decremented to hardware limits automatically.
    fheight, fwidth = _getResolution()
    cap.set(3, fheight)
    cap.set(4, fwidth)

    #Since hardware will limit possible resolution, height/width will be updated.
    fheight, fwidth = int( cap.get(cv2.CAP_PROP_FRAME_HEIGHT) ), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) ) 
    print("===Resolution height is:", fheight)
    print("===Resolution width is:", fwidth)

    #Get camera FPS5
    fps = cap.get(5)
    print("===FPS is: ",fps)
    
    print("The Esc key can be used to exit the feed.")
    
    #Create/check for a directory
    dir_path, video_count = _getFirstDirectory()
    current_path = dir_path+"\output_"+str(video_count)+".avi"

    #Codec specifcation and a VideoWriter object to save the proccessed frames.
    #Different OS will require different fourcc codes. DIVX is for Windows
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    output = cv2.VideoWriter(current_path, fourcc, fps, (fwidth, fheight))

    #The last frame processed
    last_frame = None
    

    #Video Capture happens here
    while(cap.isOpened()):
        
        #Get a frame
        check, frame = cap.read()

        if check == True:
            
            #Convert to grayscale and blur
            blurred = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(blurred, (11, 11), 0)

            #Check if this is the first frame for processing and assign.
            if last_frame is None:
                last_frame = blurred
                continue

            #Get absdifference between the two frames
            fdiff = cv2.absdiff(last_frame, blurred)

            #Set the threshold amounts
            thresh = cv2.threshold(fdiff, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations = 2)

            #Find the countour differences due to moving object
            (conts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            #Check if any movement is large enough to label as an object
            for contour in conts:
                if cv2.contourArea(contour) < MIN_MOVE_AREA:
                    continue

                #Motion has been detected
                (x, y, w, h) = cv2.boundingRect(contour)

                #Place bounding box
                cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 3)
            
            
            #Write out frame
            output.write(frame)

            #Display the frame in a window
            cv2.imshow("Filtered", blurred)
            cv2.imshow("Difference", fdiff)
            cv2.imshow("Threshold", thresh)
            cv2.imshow("Colored", frame)

            #Check for an exit; Esc is set as the exit key
            if cv2.waitKey(1) == 27:
                break
        else:
            break

    #When done the entirety of the capture will be released
    cap.release()
    output.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

if __name__ == "__main__":
    main()
