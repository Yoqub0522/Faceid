import face_recognition
import numpy as np
import cv2
import base64

def test_encoding(base64_image):
    img_data = base64.b64decode(base64_image.split(',')[1])
    np_arr = np.frombuffer(img_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    face_locations = face_recognition.face_locations(image)
    print("Yuzlar soni:", len(face_locations))  # <-- shu chiqsin

    if len(face_locations) == 0:
        print("❌ Yuz topilmadi.")
        return None

    encoding = face_recognition.face_encodings(image, face_locations)[0]
    print("✅ Encoding uzunligi:", len(encoding))
    print(encoding[:10])  # bir qismini ko‘ramiz

test_encoding(base64_str)  # bu yerga sizning base64 yuborilgan rasmi
