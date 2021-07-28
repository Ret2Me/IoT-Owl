# -*- coding: utf-8 -*-

import faceDetection.ms_face_detection
import os
import sys
from csv import reader
import json
sys.path.append(os.getcwd())

def greetUser(detected_persons):

    print(json.dumps(detected_persons, indent=4, sort_keys=True))
    # user info structure in my database:
    # 1. name
    # 2. surname 
    # 3. class 
    # 4. birthday date for special greetings in birthday

    student_info = ["", "", ""]
    greetings    = ["Good morning"]
    if len(detected_persons) != 0:
        if "userData" in detected_persons[0][0] and "confidence" in detected_persons[0][0]:
            if detected_persons[0][0]["confidence"] > 0.5:
                student_info = []
                greetings = []
                student_info = list(reader(detected_persons[0][0]["userData"]))
                greetings.append("Good morning " + str(student_info[0]))
        
        if "faceAttributes" in detected_persons[0][0]:
            if "glasses" in detected_persons[0][0]["faceAttributes"]:
                if str(detected_persons[0][0]["faceAttributes"]["glasses"]) == "Sunglasses":
                    greetings.append("Please take off your glasses " + student_info[0])
                elif detected_persons[0][0]["faceAttributes"]["glasses"] == "ReadingGlasses":
                    greetings.append("You looks good with this glasses " + str(student_info[0]))

                if detected_persons[0][0]["faceAttributes"]["smile"] > 0.6:
                    greetings.append("Nice smile " + str(student_info[0]))
            else:
                if detected_persons[0][0]["faceAttributes"]["mask"]["noseAndMouthCovered"] == False:
                    greetings = "Good morning " + str(student_info[0]) + " please correct the face mask"
        print(json.dumps(detected_persons, indent=4, sort_keys=True))
        print(greetings)
        # now you can display or speak one of the texts from greetings list

def experimental():
    # run face detection at new thread
    test = faceDetection.ms_face_detection.APIFaceDetection()
    test.run(greetUser)

if __name__ == "__main__":
    # main()
    experimental()  