from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import json

def main(movie_path):
    movie_clip = VideoFileClip(movie_path)
    json_path = movie_path.replace(".mp4", ".json")
    with open(json_path, encoding="utf-8") as fp:
        data = json.load(fp)
    fps = data["fps"]

    clips = [movie_clip]
    for frame_idx, flow_scores in zip(data["frames"], data["optical_flow"]):
        txt_clip = TextClip(f"{flow_scores:.02f}" ,fontsize=70, color='green')
        txt_clip = txt_clip.set_pos(("center", 'top')).set_duration(1).set_start(int(frame_idx)//fps)
        clips.append(txt_clip)

    video = CompositeVideoClip(clips)
    video.write_videofile("joint_movie.mp4")

if __name__ == "__main__":
    main("video/暴れん坊将軍のテーマ [nBXX-RT38uQ].mp4")