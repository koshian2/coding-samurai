from yt_dlp import YoutubeDL
import moviepy.editor as mpe
import plotly.express as px
import numpy as np
from pydantic import BaseModel
from typing import List
import moviepy.editor as mpe
import uuid
import os
import shutil
import ml

VIDEO_CLIP_PATH = "tmp"

class SectionState(BaseModel):
    id: int
    score: float = 0
    start_seconds: int = 0
    end_seconds: int = 0
    
    def get_into(self):
        return f"""### Top{self.id+1}  
* score : {self.score:.02f}
* start[min] : {self.start_seconds / 60}
* end[min] : {self.end_seconds / 60}
"""

class AppState(BaseModel):
    sections: List[SectionState] = []
    session_id: str = ""
    local_video_path: str = ""
    video_url: str = ""

    def get_session_id(self):
        if self.session_id == "":
            self.session_id = str(uuid.uuid4())
        return self.session_id

    def assign_section_states(self, minutes: np.ndarray, scores: np.ndarray):
        items = []
        for i, (minute, score) in enumerate(zip(minutes, scores)):
            item = SectionState(
                id=i, score=score, start_seconds=minute*60, end_seconds=(minute+1)*60
            )
            items.append(item)
        self.sections = items

def download_youtube(url: str, download_root_directory: str): 
    ydl_opts = {
        "format": "best",
        'outtmpl': f'{download_root_directory}/%(title)s [%(id)s].%(ext)s' 
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        file_path = ydl.prepare_filename(info_dict)
        result = ydl.download([url])
    return file_path

def process_video(url_text: str, 
                  state: AppState,                  
                  window_size: int=60):
    # remove video clips directory
    root_dir = os.path.join(VIDEO_CLIP_PATH, state.get_session_id())
    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)
    # download youtube
    state.video_url = url_text
    state.local_video_path = download_youtube(url_text, root_dir)
    # ML processing
    raw_frame_nums, raw_flow_scores, windowed_frame_nums, windowed_flow_scores, fps \
        = ml.run_raft(state.local_video_path, window=window_size)
    # raw_score graph
    fig_raw = px.bar(x=raw_frame_nums, y=raw_flow_scores, labels={"x":"seconds", "y":"flow score"})
    # windowed score graph
    fig_windowed = px.bar(x=windowed_frame_nums, y=windowed_flow_scores, labels={"x":"minites", "y":"flow score"})
    # windowed score view (top 10)
    minutes = np.argsort(windowed_flow_scores)[::-1][:10]
    top_scores = np.array(windowed_flow_scores)[minutes]
    message = ["### Parse Info"] + [f"Top {i+1} Section : {minutes[i]}:00-{minutes[i]+1}:00" for i in range(len(minutes))]
    message = "  \n".join(message)
    # assign to state
    state.assign_section_states(minutes, top_scores)

    return state.local_video_path, fig_raw, fig_windowed, message, state

def play_section(state: AppState, section_idx: int):
    if section_idx >= len(state.sections):
        return None, ""
    # extract video
    item = state.sections[section_idx]
    out_path = os.path.join(VIDEO_CLIP_PATH, state.get_session_id(), 
                            f"{item.id}_{item.start_seconds:05}_{item.end_seconds:05}.mp4")
    if not os.path.exists(out_path):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        videoclip = mpe.VideoFileClip(state.local_video_path)
        subclip = videoclip.subclip(item.start_seconds, min(item.end_seconds, videoclip.duration))
        subclip.write_videofile(out_path)
    # section info
    info = state.sections[section_idx].get_into()
    return out_path, info