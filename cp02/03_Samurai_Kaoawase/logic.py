import mediapipe as mp
from PIL import Image
import numpy as np
from typing import List
from pydantic import BaseModel
import glob
import os

class GameState(BaseModel):
    samurai_paths : List[str] = [] # 侍の画像のパス
    samurai_names : List[str] = [] # 侍の名前
    samurai_max_scores : dict = {
        "Easy": [],
        "Normal": [],
        "Hard": []
    } # 難易度単位の侍ごとの最高スコア
    samurai_index : int = 0 # 侍のインデックス
    difficulty : str = "Normal" # 難易度

    def initialize_states(self):
        self.samurai_paths = glob.glob("imgs/*")
        self.samurai_names = [os.path.splitext(os.path.basename(path))[0] for path in self.samurai_paths]
        for difficulty in self.samurai_max_scores:
            self.samurai_max_scores[difficulty] = [0] * len(self.samurai_names)

def detect_facial_landmark(orig_img: Image):
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        min_detection_confidence=0.3) as face_mesh:

        img = orig_img.convert("RGB")
        img = np.array(img)
        result = face_mesh.process(img)
    # Keypointの座標のarrayにする
    positions = []
    if result.multi_face_landmarks is None:
        return np.array(positions)
    for face_landmarks in result.multi_face_landmarks:
        if face_landmarks is None:
            continue
        for landmark in face_landmarks.landmark:
            positions.append([landmark.x, landmark.y])
    return np.array(positions)
    
def normalize_array(input_array: np.ndarray):
    min_values = np.min(input_array, axis=0, keepdims=True)
    max_values = np.max(input_array, axis=0, keepdims=True)
    normalized_array = (input_array - min_values) / (max_values - min_values)
    return normalized_array

def compute_scores(ref_result: np.ndarray,
                   camera_result: np.ndarray, 
                   state: GameState):
    ref_result_norm = normalize_array(ref_result)
    camera_result_norm = normalize_array(camera_result)
    diff = np.linalg.norm(ref_result_norm - camera_result_norm, axis=-1)
    if state.difficulty == "Easy":
        ratio = 100
    elif state.difficulty == "Normal":
        ratio = 300
    else:
        ratio = 500
    score = int(np.maximum(100 - np.mean(diff) * ratio, 0))
    # set max score to state
    state.samurai_max_scores[state.difficulty][state.samurai_index] = \
        max(state.samurai_max_scores[state.difficulty][state.samurai_index], score)
    return score

if __name__ == "__main__":
    with Image.open("imgs/フランシスコ・ザビエル.png") as img:
        results = detect_facial_landmark(img)
        print(results.shape)
