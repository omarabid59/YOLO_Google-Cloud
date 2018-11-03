import cv2

def detect(img, cascade):
  gray = to_grayscale(img)
  rects = cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)

  if len(rects) == 0:
    return []
  return rects

def detect_faces(img):
  cascade = cv2.CascadeClassifier("/home/omar_abid4_gmail_com/cloud_ml_webrtc/data/haarcascade_frontalface_alt.xml")
  return detect(img, cascade)

def to_grayscale(img):
  gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
  gray = cv2.equalizeHist(gray)
  return gray
