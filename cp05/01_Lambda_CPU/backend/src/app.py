import open_clip
import base64
import io
from PIL import Image
import torch

models = None

def get_models():
    global models
    if models is None:
        model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-16-SigLIP", pretrained="webli", cache_dir="/tmp")
        tokenizer = open_clip.get_tokenizer("ViT-B-16-SigLIP")
        models = (model, preprocess, tokenizer)
    return models

def lambda_handler(event, context):
    model, preprocess, tokenizer = get_models()
    # extract data
    img = Image.open(io.BytesIO(base64.b64decode(event["image"]))) # Input image
    prompt = [x.strip() for x in event["prompt"].split(",")]
    # preprcess
    img = preprocess(img).unsqueeze(0)
    text = tokenizer(prompt)

    # Run CLIP
    with torch.no_grad():
        image_features = model.encode_image(img)
        text_features = model.encode_text(text)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1).numpy()[0]

    # return result
    text_probs = text_probs.tolist()
    return text_probs
