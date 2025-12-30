import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera not detected")
    exit()

ret, frame = cap.read()
if ret:
    print("Frame captured successfully!")
    cv2.imwrite("test_image.jpg", frame)
else:
    print("Could not grab frame")

cap.release()
