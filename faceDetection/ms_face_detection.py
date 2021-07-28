from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import cvlib as cv
import cv2
import time
from threading import Thread
import requests
import json
import io
import matplotlib.pyplot as plt
from os.path import isfile 
import config
import numpy as np
import time


class ThreadedCamera(Thread):
    def __init__(self, source = 0):

        self.capture = cv2.VideoCapture(source)

        self.thread = Thread(target = self.update, args = ())
        self.thread.daemon = True
        self.thread.start()

        self.status = False
        self.c_frame  = None

    def update(self):
        while True:
            if self.capture.isOpened():
                (self.status, self.c_frame) = self.capture.read()

    def grab_frame(self):
        if self.status:
            return self.c_frame
        return None  


def detect_and_predict_mask(frame, faceNet, maskNet):
        # grab the dimensions of the frame and then construct a blob
        # from it
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
            (104.0, 177.0, 123.0))

        # pass the blob through the network and obtain the face detections
        faceNet.setInput(blob)
        detections = faceNet.forward()

        # initialize our list of faces, their corresponding locations,
        # and the list of predictions from our face mask network
        faces = []
        locs = []
        preds = []

        # loop over the detections
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the detection
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the confidence is
            # greater than the minimum confidence
            if confidence > config.MASK_CONF:
                # compute the (x, y)-coordinates of the bounding box for
                # the object
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # ensure the bounding boxes fall within the dimensions of
                # the frame
                (startX, startY) = (max(0, startX), max(0, startY))
                (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

                # extract the face ROI, convert it from BGR to RGB channel
                # ordering, resize it to 224x224, and preprocess it
                face = frame[startY:endY, startX:endX]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = cv2.resize(face, (224, 224))
                face = img_to_array(face)
                face = preprocess_input(face)

                # add the face and bounding boxes to their respective
                # lists
                faces.append(face)
                locs.append((startX, startY, endX, endY))

        # only make a predictions if at least one face was detected
        if len(faces) > 0:
            # for faster inference we'll make batch predictions on *all*
            # faces at the same time rather than one-by-one predictions
            # in the above `for` loop
            faces = np.array(faces, dtype="float32")
            preds = maskNet.predict(faces, batch_size=32)

        # return a 2-tuple of the face locations and their corresponding
        # locations
        return (locs, preds)


# face detection based on Face API provided by Microsoft  
class APIFaceDetection(object):
    def __init__(self):

        # Return values
        self.__info_about_student = []
        self.__prototxtPath = "faceDetection/models/deploy.prototxt"
        self.__weightsPath = "faceDetection/models/res10_300x300_ssd_iter_140000.caffemodel"
        self.__faceNet = cv2.dnn.readNet(self.__prototxtPath, self.__weightsPath)

        self.__maskNet = load_model("faceDetection/models/mask_detector.model")
        # initialize db with students
        if isfile('students.db') == False:
            write_database = open(config.DATABASE_NAME, 'x')
            headers = {
            'Ocp-Apim-Subscription-Key': config.SUBSCRIPTION_KEY
            }


            database = requests.request("GET", url=config.FACELISTS_URL, headers=headers)
            if database.status_code != 200:
                print("[ERROR] Unable to download database\r\n") 
                print(database.text)
                exit


            write_database.write(database.text)
            write_database.close()
            self.__local_database = database.json()
    
        else:
            open_database = open('students.db', 'r')
            self.__local_database = json.loads(open_database.read())
            open_database.close()

    
    def run(self, function2run):
        # open webcam
        try:
            streamer = ThreadedCamera(config.STREAM_LINK)
        except:
            print("Missing STREAM_LINK in configuration file")


        last_face_check   = time.time()
        best_result       = 0  
        frame_number      = 0
        best_photo        = [] 
        best_photo_startX = 0 
        best_photo_endX   = 0
        best_photo_startY = 0
        best_photo_endY   = 0 
        frame             = None

        i = 0 
        while True: #webcam.isOpened():
            frame = streamer.grab_frame()
           
            if frame is None:
                continue


            # apply face detection
            face, confidence = cv.detect_face(frame)
            
            # loop through detected faces
            for idx, f in enumerate(face): 
                (startX, startY) = f[0], f[1]
                (endX, endY) = f[2], f[3]

                    
                if time.time() - last_face_check < config.API_CALL_COOLDOWN:
                    function2run(detected_persons = [])
                    time.sleep(config.FUNCTION_CALL_COOLDOWN)
                    continue

                if best_result < confidence[idx]:

                    #save best frame to buffer 
                    best_result = confidence[idx]                    
                    best_photo = frame
                    

                    # save face postion at best frame 
                    best_photo_startX = startX 
                    best_photo_endX   = endX
                    best_photo_startY = startY
                    best_photo_endY   = endY
                    if best_result * 100 > 99:
                        frame_number = config.FRAMES_TO_ANALYZE


                if frame_number == config.FRAMES_TO_ANALYZE:                
                    frame_number = 0 
                    i += 1
                    # send photo to analize  
                    if best_result * 100 > 80:
                        # text to display in frame
                        last_face_check = time.time()
                        h, w, c = best_photo.shape


                        # if part of the face is outside of the frame 
                        # it will set starting point at first element of frame or last element of frame
                        if startY < 0: 
                            startY = 0
                        if endY > h:
                            endY = h - 1
                        if startX < 0:
                            startX = 0 
                        if endX > w:
                            endX = w - 1


                        # checks is it possible to extend face img 
                        if startY - config.ADDITIONAL_SPACE > 0:
                            best_photo_startY = startY - config.ADDITIONAL_SPACE
                        if endY + config.ADDITIONAL_SPACE >= h:
                            best_photo_endY = endY + config.ADDITIONAL_SPACE
                        if startX - config.ADDITIONAL_SPACE >= 0:
                            best_photo_startX = startX - config.ADDITIONAL_SPACE
                        if endX + config.ADDITIONAL_SPACE >= 0:
                            best_photo_endX = endX + config.ADDITIONAL_SPACE

                        
                        # crop face 
                        best_photo = best_photo[best_photo_startY: best_photo_endY, best_photo_startX:best_photo_endX]
                        h, w, c = best_photo.shape
                                                
                        if best_photo is None or h <= 36 or w <= 36:
                            continue
                            
                        # save copy of cropped frame to buffer and disk  
                        img_buffer = io.BytesIO() 
                        plt.imsave(img_buffer, best_photo, format='jpg')


                        (locs, preds) = detect_and_predict_mask(frame, self.__faceNet, self.__maskNet)
                        (mask, withoutMask) = preds[0]


                        # check is person in the picture is wearing mask 
                        if mask >= withoutMask:
                            request_url = config.MSFACE_API_URL_WITH_MASK
                            find_similar_list_id = config.FACE_WITH_MASK_LIST_ID
                        else:
                            request_url = config.MSFACE_API_URL 
                            find_similar_list_id = config.FACE_LIST_ID

                        # request header
                        msface_api_header = {
                            'Content-Type': 'application/octet-stream',
                            'Ocp-Apim-Subscription-Key': config.SUBSCRIPTION_KEY
                        }
                        

                        # send request
                        response = requests.request("POST", url=request_url, headers=msface_api_header, data=img_buffer.getvalue())
                        student_info = response.json()
                        
                        
                        if response.status_code != 200:
                            print("[ERROR] request to: ", config.FINDSIMILARS_URL, " failed")
                            print(response.text)
                            print(response)
                        if len(student_info) == 0:
                            print("Face not detected")
                            img_buffer = io.BytesIO() 
                            plt.imsave(img_buffer, frame, format='jpg')

                            # uncomment if you want to save image where ms didn't detect user but local library does   
                            # cv2.imwrite('logs/best_photo_1.jpg', best_photo)

                            response = requests.request("POST", url=request_url, headers=msface_api_header, data=img_buffer.getvalue()) #, data=best_photo
                            student_info = response.json()
                            print("------- whole frame -------")
                            best_result = 0
                            frame_number += 1
                            continue 


                        self.__info_about_student = student_info
                        payload = "{ \"faceId\": \""
                        payload += str(student_info[0]["faceId"])
                        payload += "\",\r\n\"faceListId\": \""
                        payload += find_similar_list_id
                        payload += "\",\r\n\"maxNumOfCandidatesReturned\": 1,\r\n\"mode\": \"matchPerson\"\r\n}"
                        headers = {
                            'Ocp-Apim-Subscription-Key': config.SUBSCRIPTION_KEY,
                            'Content-Type': 'application/json'
                        }


                        student_id = requests.request("POST", url=config.FINDSIMILARS_URL, headers=headers, data=payload)
                        json_student_id = student_id.json()
                        if student_id.status_code != 200:
                            print("[ERROR] request to: ", config.FINDSIMILARS_URL, " failed")
                            print(response.text)
                            print(response)                        
                        if len(json_student_id) == 0:
                            print("Can't recognize student")
                            function2run(detected_persons = [self.__info_about_student])
                            best_result = 0
                            frame_number += 1
                            continue 
                        else:
                            self.__info_about_student[0]["confidence"] = json_student_id[0]["confidence"]


                        # looking for matchs person in local database
                        for person in self.__local_database["persistedFaces"]:
                            if person["persistedFaceId"] == json_student_id[0]["persistedFaceId"]:
                                if request_url != config.MSFACE_API_URL_WITH_MASK:
                                    self.__info_about_student[0]["userData"] = person["userData"] 
                                else:
                                    self.__info_about_student[0]["userData"] = person["mask"] 
                        print(time.time() - last_face_check)
                        function2run(detected_persons = [self.__info_about_student])
                        self.__info_about_student = None 
                    best_result = 0
                frame_number += 1