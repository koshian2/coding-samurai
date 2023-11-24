import plotly.express as px
import json
import numpy as np
from pydantic import BaseModel
from typing import List
import moviepy.editor as mpe
import uuid
import os
import shutil

VIDEO_CLIP_PATH = "tmp"

class SectionState(BaseModel):
    id: int
    score: float = 0
    start_seconds: int = 0
    end_seconds: int = 0

    def extract_video(self, parent_state):
        out_path = f"{VIDEO_CLIP_PATH}/{parent_state.get_session_id()}/{self.id}_{self.start_seconds:05}_{self.end_seconds:05}.mp4"
        if not os.path.exists(out_path):
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            videoclip = mpe.VideoFileClip(parent_state.local_video_path)
            subclip = videoclip.subclip(self.start_seconds, min(self.end_seconds, videoclip.duration))
            subclip.write_videofile(out_path)
        return out_path
    
    def get_into(self):
        return f"""### Top{self.id+1}  
* score : {self.score:.02f}
* start[min] : {self.start_seconds / 60}
* end[min] : {self.end_seconds / 60}
"""

class AppState(BaseModel):
    sections: List[SectionState] = []
    session_id: str = ""
    local_video_path: str = "../work/video/暴れん坊将軍のテーマ [nBXX-RT38uQ].mp4"

    def assign_section_states(self, minutes: np.ndarray, scores: np.ndarray):
        items = []
        for i, (minute, score) in enumerate(zip(minutes, scores)):
            item = SectionState(
                id=i, score=score, start_seconds=minute*60, end_seconds=(minute+1)*60
            )
            items.append(item)
        self.sections = items

    def get_session_id(self):
        if self.session_id == "":
            self.session_id = str(uuid.uuid4())
        return self.session_id

def process_video(url_text: str, 
                  state: AppState,                  
                  window_size: int=60):
    with open("../work/video/暴れん坊将軍のテーマ [nBXX-RT38uQ].json", encoding="utf-8") as fp:
        flow_data = json.load(fp)
    # remove video clips directory
    if os.path.exists(f"{VIDEO_CLIP_PATH}/{state.get_session_id()}"):
        shutil.rmtree(f"{VIDEO_CLIP_PATH}/{state.get_session_id()}")        
    # raw_score graph
    fig_raw = px.bar(x=flow_data["frames"], y=flow_data["optical_flow"], labels={"x":"seconds", "y":"flow score"})
    # windowed score graph
    windowed_frames, windowed_score = [], []
    for i in range(len(flow_data["frames"])//60 + 1):
        windowed_frames.append(i)
        windowed_score.append(np.mean(flow_data["optical_flow"][i*60:(i+1)*60]))
    fig_windowed = px.bar(x=windowed_frames, y=windowed_score, labels={"x":"minites", "y":"flow score"})
    # windowed score view (top 10)
    minutes = np.argsort(windowed_score)[::-1][:10]
    top_scores = np.array(windowed_score)[minutes]
    message = ["### Parse Info"] + [f"Top {i+1} Section : {minutes[i]}:00-{minutes[i]+1}:00" for i in range(len(minutes))]
    # assign to state
    state.assign_section_states(minutes, top_scores)

    return state.local_video_path, fig_raw, fig_windowed, "  \n".join(message), state

def play_section(state: AppState, section_idx: int):
    if section_idx >= len(state.sections):
        return None, ""
    filename = state.sections[section_idx].extract_video(state)
    info = state.sections[section_idx].get_into()
    return filename, info