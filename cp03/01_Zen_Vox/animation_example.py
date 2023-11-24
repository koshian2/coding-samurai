import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time

def animation(container):
    bg_color = np.random.randint(0, 255, size=(3,))
    fg_color = np.zeros_like(bg_color) if np.mean(bg_color) > 127 else np.full_like(bg_color, 255)
    font = ImageFont.truetype('arial.ttf', 18)
    with Image.new("RGB", (100, 100), tuple(bg_color.tolist())) as canvas:
        for i in range(5):
            img = canvas.copy()
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), f"{4-i}", tuple(fg_color.tolist()), font=font)
            container.image(np.array(img))
            time.sleep(1)
        st.session_state["images"].append(np.array(img))

def main():
    if "images" not in st.session_state:
        st.session_state["images"] = []
    
    for img in st.session_state["images"]:
        st.image(img)

    button = st.button("click")
    if button:
        container = st.empty()
        animation(container)

if __name__ == "__main__":
    main()