from yt_dlp import YoutubeDL
import plotly.express as px
import numpy as np
from pydantic import BaseModel
from typing import List, Any
import requests
import json
import uuid
import os
import shutil
import aws

def get_video_clip_path():
    if "RUN_ENV" not in os.environ.keys() or os.environ["RUN_ENV"] == "host":
        return "tmp"
    else:
        return "/tmp"

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
    success_file_key: str = ""
    failure_file_key: str = ""
    input_file_key: str = ""

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

def download_video(url_text: str, state: AppState):
    # remove video clips directory
    root_dir = os.path.join(get_video_clip_path(), state.get_session_id())
    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)
    # download youtube
    state.video_url = url_text
    ydl_opts = {
        "format": "best",
        'outtmpl': f'{root_dir}/%(title)s [%(id)s].%(ext)s' 
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url_text, download=False)
        state.local_video_path = ydl.prepare_filename(info_dict)
        _ = ydl.download([url_text])
    return state.local_video_path, state

def update_ui(result: dict,
              state: AppState):
    raw_frame_nums, raw_flow_scores, windowed_frame_nums, windowed_flow_scores \
        = result["raw_frame_nums"], result["raw_flow_scores"], result["windowed_frame_nums"], result["windowed_flow_scores"]
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

    return fig_raw, fig_windowed, message, state

def process_video(state: AppState,                  
                  window_size: int=60):
    # ML processing
    if "RUN_ENV" in os.environ.keys() and os.environ["RUN_ENV"] == "aws":
        response = aws.run_inference(state.local_video_path)
        state.success_file_key = response["success_file_key"]
        state.failure_file_key = response["failure_file_key"]
        state.input_file_key = response["input_file_key"]
        if response["status"] == "success":
            result = response["content"]
        else:
            return None, None, response["content"], state
    else:
        with open(state.local_video_path, "rb") as fp:
            payload = fp.read()
        if "RUN_ENV" not in os.environ.keys() or os.environ["RUN_ENV"] == "host":
            response = requests.post("http://127.0.0.1:9011/invocations", 
                                    data=payload)
            response = response.text
        elif os.environ["RUN_ENV"] == "docker":
            response = requests.post("http://host.docker.internal:9011/invocations", 
                                    data=payload)
            response = response.text
        else:
            raise NotImplementedError()
        result = json.loads(response)
    
    return update_ui(result, state)


def redownload_result(fig_raw: Any,
                      fig_windowed: Any,
                      message: str,
                      state: AppState):
    if "RUN_ENV" in os.environ.keys() and os.environ["RUN_ENV"] == "aws":
        response = aws.exponential_polling(state.success_file_key,
                                           state.failure_file_key,
                                           state.input_file_key)
        state.success_file_key = response["success_file_key"]
        state.failure_file_key = response["failure_file_key"]
        state.input_file_key = response["input_file_key"]
        if response["status"] == "success":
            result = response["content"]
        else:
            return fig_raw, fig_windowed, response["content"], state
    else:
        # return inputs directly
        return fig_raw, fig_windowed, message, state

    return update_ui(result, state)

def play_section(state: AppState, section_idx: int):
    if section_idx >= len(state.sections):
        return None, ""
    # extract video
    item = state.sections[section_idx]
    out_path = os.path.join(get_video_clip_path(), state.get_session_id(), 
                            f"{item.id}_{item.start_seconds:05}_{item.end_seconds:05}.mp4")
    if not os.path.exists(out_path):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        if "RUN_ENV" in os.environ.keys() and os.environ["RUN_ENV"] == "aws":
            aws.run_video_clip(out_path, state.input_file_key,
                               item.start_seconds, item.end_seconds)
        else:
            if "RUN_ENV" not in os.environ.keys() or os.environ["RUN_ENV"] == "host":
                import moviepy.editor as mpe
                videoclip = mpe.VideoFileClip(state.local_video_path)
                subclip = videoclip.subclip(item.start_seconds, min(item.end_seconds, videoclip.duration))
                subclip.write_videofile(out_path)
            elif os.environ["RUN_ENV"] == "docker":
                aws.run_video_clip_locally(state.local_video_path, "edoflow/input",
                                           out_path, item.start_seconds, item.end_seconds)
            else:
                raise NotImplementedError()        
    # section info
    info = state.sections[section_idx].get_into()
    return out_path, info