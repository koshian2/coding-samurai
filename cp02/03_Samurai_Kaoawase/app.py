import gradio as gr
import logic
import random
from PIL import Image

def get_samurai_header(state: logic.GameState):
    samurai_name = state.samurai_names[state.samurai_index]
    max_score = state.samurai_max_scores[state.difficulty][state.samurai_index]
    total_scores = sum(state.samurai_max_scores[state.difficulty])
    return f"## {samurai_name} | 最高点: {max_score} | 合計点: {total_scores}"

def random_loading(state: logic.GameState):
    if state.samurai_names == []:
        state.initialize_states()
    state.samurai_index = random.choice(range(len(state.samurai_names)))
    img_file = state.samurai_paths[state.samurai_index]
    header_message = get_samurai_header(state)
    return img_file, header_message, state

def change_difficulty(new_difficulty: str,
                      state: logic.GameState):
    state.difficulty = new_difficulty
    return get_samurai_header(state), state

def shot(reference_image: Image,
         camera_image: Image,
         state: logic.GameState):
    if reference_image is None or camera_image is None:
        return "", "", state
    # compute scores
    reference_result = logic.detect_facial_landmark(reference_image)
    camera_result = logic.detect_facial_landmark(camera_image)
    # if can't get facial key points
    if reference_result.shape[0] == 0 or camera_result.shape[0] == 0:
        return get_samurai_header(state), "## カメラから顔を検出できませんでした", state

    score = logic.compute_scores(reference_result, camera_result, state)
    # Message
    header_message = get_samurai_header(state)
    score_message = f"## あなたの {state.samurai_names[state.samurai_index]} 度は {score} 点です"
    return header_message, score_message, state

with gr.Blocks() as demo:
    gr.Markdown("<h1 align='center'> 🗡️侍顔合わせ👹 </h1>")
    gr.Markdown("<div align='center'>あなたの顔は伝説の侍にどれだけ似ている？　武士の血が流れているかチェックしよう！</div>")
    with gr.Row():
        with gr.Column():
            reference_header = gr.Markdown()
            reference_image = gr.Image(label="侍画像", type="pil")
            button_change = gr.Button("侍を召喚", variant="primary")
            difficulty = gr.Radio(["Easy", "Normal", "Hard"], label="難易度", value="Normal")
            score_message = gr.Markdown()
        with gr.Column():
            camera_image = gr.Image(label="あなたのカメラ", type="pil", sources=["webcam"], streaming=True) # Gradio Ver4
            # camera_image = gr.Image(label="あなたのカメラ", type="pil", source="webcam", streaming=True) # Gradio Ver3
            button_shot = gr.Button("顔合わせ")

    state = gr.State(logic.GameState())
    gr.Markdown("<div align='right'>Webカメラが必要です。スコアをリセットするには再読み込みしてください</div>")
    
    # Event Handler
    difficulty.change(change_difficulty, [difficulty, state], [reference_header, state])
    button_change.click(random_loading, 
                        state, [reference_image, reference_header, state])
    button_shot.click(shot, 
                        [reference_image, camera_image, state],
                        [reference_header, score_message, state])

if __name__ == "__main__":
    demo.launch()