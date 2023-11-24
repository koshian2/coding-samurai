import open_clip
from PIL import Image
import torch

def main():
    model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-16-SigLIP", pretrained="webli")
    img = preprocess(Image.open("imgs/DT306017.jpg")).unsqueeze(0)
    tokenizer = open_clip.get_tokenizer("ViT-B-16-SigLIP")
    text = tokenizer(["a sword", "a shield", "an armor", "a helmet"])

    # Run CLIP
    with torch.no_grad():
        image_features = model.encode_image(img)
        text_features = model.encode_text(text)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1).numpy()
        print(text_probs)

if __name__ == "__main__":
    main()