import gradio as gr
import logic
import functools
import os

with gr.Blocks() as demo:
    gr.Markdown("<h1 align='center'>🎥👘 EdoFlow Highlighter🔍✨</h1>")
    with gr.Row():
        with gr.Column():
            youtube_url = gr.Textbox(label="YouTube URL")
            button_dl = gr.Button("Download")
            button_parse = gr.Button("Parse")
            button_redownload = gr.Button("Redownload Parsed Result")
            all_video = gr.Video(label="All Video", interactive=False)
        with gr.Column():
            flowscore_raw_fig = gr.Plot(label="Flow Score")
        with gr.Column():
            flowscore_window_fig = gr.Plot(label="Flow Score (windowed)")
    section_buttons = []
    with gr.Row():
        for i in range(5):
            section_buttons.append(gr.Button(f"Top {i+1}"))
    with gr.Row():
        for i in range(5, 10):
            section_buttons.append(gr.Button(f"Top {i+1}"))
    with gr.Row():
        with gr.Column(scale=1):
            parse_info = gr.Markdown("")
            section_info = gr.Markdown("")
        with gr.Column(scale=5):
            section_video = gr.PlayableVideo(label="Section Video", interactive=False)
    state = gr.State(logic.AppState())

    for i in range(len(section_buttons)):
        section_buttons[i].click(functools.partial(logic.play_section, section_idx=i), [state], [section_video, section_info])
 
    button_dl.click(logic.download_video, [youtube_url, state], 
                    [all_video, state])
    ui_components = [flowscore_raw_fig, flowscore_window_fig, parse_info, state]
    button_parse.click(logic.process_video, [state], ui_components)
    button_redownload.click(logic.redownload_result, ui_components, ui_components)

if __name__ == "__main__":
    if "RUN_ENV" not in os.environ.keys() or os.environ["RUN_ENV"] == "host":
        demo.launch()
    else:
        demo.launch(server_name="0.0.0.0", server_port=8080)