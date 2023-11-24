from pydantic import BaseModel
import random
import gradio as gr

class GameState(BaseModel):
    player_current_hp : int = 50
    player_max_hp : int = 50
    player_attack : int = 20
    enemy_hp : int = 1000
    enemy_attack : int = 10
    is_player_dead : bool = False
    is_enemy_dead : bool = False

def attack(state: GameState):
    player_damage = random.randint(int(state.player_attack*0.8), int(state.player_attack*1.2))
    enemy_damage = random.randint(int(state.enemy_attack*0.8), int(state.enemy_attack*1.2))
    state.enemy_hp -= player_damage
    state.player_current_hp -= enemy_damage
    message = f"Player -> Enemy : {player_damage} Damage !  \n"
    message += f"Enemy -> Player : {enemy_damage} Damage !  \n"
    if state.enemy_hp <= 0:
        state.enemy_hp = 0
        state.is_enemy_dead = True
        message += "Enemy is dead! You Win!"
    if state.player_current_hp <= 0:
        state.player_current_hp = 0
        state.is_player_dead = True
        message += "Player is dead! You Lose!"
    return state, message

def cure(state: GameState):
    cure_hp = random.randint(int(state.player_max_hp*0.5), int(state.player_max_hp*1.0))
    ememy_damage = random.randint(int(state.enemy_attack*0.8), int(state.enemy_attack*1.2))
    state.player_current_hp -= ememy_damage
    state.player_current_hp = min(cure_hp + state.player_current_hp, state.player_max_hp)
    message = f"Enemy -> Player : {ememy_damage} Damage !  \n"
    message += f"Player cure {cure_hp} HP !  \n"
    return state, message

def update_ui(state: GameState):
    button_enable = not(state.is_enemy_dead or state.is_player_dead)
    return state.player_current_hp, state.enemy_hp, gr.update(interactive=button_enable), gr.update(interactive=button_enable)

with gr.Blocks() as demo:
    gr.Markdown("<h1 align='center'>Simple RPG</h1>")
    with gr.Row():
        with gr.Column():
            enemy_hp = gr.Slider(label="Enemy HP", interactive=False, maximum=1000, minimum=0, value=1000)
        with gr.Column():
            player_hp = gr.Slider(label="Player HP", interactive=False, maximum=50, minimum=0, value=50)
    with gr.Row():
        with gr.Column():
            button_attack = gr.Button("Attack")
        with gr.Column():
            button_cure = gr.Button("Cure")
    message = gr.Markdown("")
    state = gr.State(GameState())

    button_attack.click(attack, state, [state, message]).then(
        update_ui, state, [player_hp, enemy_hp, button_attack, button_cure])
    button_cure.click(cure, state, [state, message]).then(
        update_ui, state, [player_hp, enemy_hp, button_attack, button_cure])

if __name__ == "__main__":
    demo.launch()