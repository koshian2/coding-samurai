import mediapipe as mp
from PIL import Image
import numpy as np

def enumerate_landmarks():
    mp_face_mesh = mp.solutions.face_mesh
    with Image.open("武田信玄.png") as orig_img:
        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            min_detection_confidence=0.3) as face_mesh:

            img = orig_img.convert("RGB")
            img = np.array(img)
            result = face_mesh.process(img)

        for face_landmarks in result.multi_face_landmarks:
            for landmark in face_landmarks.landmark:
                print(landmark)
    
def draw_landmarks():
    mp_drawing = mp.solutions.drawing_utils
    mp_face_mesh = mp.solutions.face_mesh
    drawing_spec = mp_drawing.DrawingSpec(thickness=2, circle_radius=2, color=(0, 255, 0))

    with Image.open("武田信玄.png") as orig_img:
        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            min_detection_confidence=0.3) as face_mesh:

            img = orig_img.convert("RGB")
            img = np.array(img)
            result = face_mesh.process(img)

        for face_landmarks in result.multi_face_landmarks:
            mp_drawing.draw_landmarks(
                image=img,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=drawing_spec)
        
        with Image.fromarray(img) as fp:
            fp.save("武田信玄_キーポイント.png")


if __name__ == "__main__":
    draw_landmarks()
