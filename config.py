            ############################
            #      FACE DETECTION      #
            ############################ 

# Face recognition based on openCV and Microsoft Face API
# ToDo: Add DETECTION_MODEL and RECOGNITION_MODEL support 
DATABASE_NAME  = 'students.db'
API_CALL_COOLDOWN = 10
FRAMES_TO_ANALYZE = 60
ADDITIONAL_SPACE = 40
CROP_IMG = True
MASK_CONF = 0.6
FUNCTION_CALL_COOLDOWN = 3 




# ToDo
# 'detection_01': 
# The default detection model for Face - Detect. Recommend for near frontal face detection.
# For scenarios with exceptionally large angle (head-pose) faces, occluded faces or wrong 
# image orientation, the faces in such cases may not be detected.
# -----------------------------------------------------------------------------------------
# 'detection_02': 
# Detection model released in 2019 May with improved accuracy especially on small, side and
# blurry faces. Face attributes and landmarks are disabled if you choose this detection model.
# -----------------------------------------------------------------------------------------
# 'detection_03': Detection model released in 2021 February with improved accuracy especially 
# on small faces. Face attributes (mask and headPose only) and landmarks are supported if 
# you choose this detection model.
DETECTION_MODEL = 3

# 'recognition_01':
# The default recognition model for Face - Detect. All those faceIds created before 2019 March 
# are bonded with this recognition model.
# -----------------------------------------------------------------------------------------
# 'recognition_02': Recognition model released in 2019 March.
# -----------------------------------------------------------------------------------------
# 'recognition_03': Recognition model released in 2020 May.
# -----------------------------------------------------------------------------------------
# 'recognition_04': Recognition model released in 2021 February. 'recognition_04' is recommended 
# since its accuracy is improved on faces wearing masks compared with 'recognition_03', and its 
# overall accuracy is improved compared with 'recognition_01' and 'recognition_02'.
RECOGNITION_MODEL = 4




#if the camera is connected directly to PC choose which one should be used (default value is "0")
STREAM_LINK = "http://192.168.1.73:4747/video/"
FACE_LIST_ID = ''
FACE_WITH_MASK_LIST_ID = ''
SUBSCRIPTION_KEY = ''


#used to detect face
MSFACE_API_URL = ""

MSFACE_API_URL_WITH_MASK = ""

# used to find similar face 
FINDSIMILARS_URL = ""


# used to download database with student faces
FACELISTS_URL = ""