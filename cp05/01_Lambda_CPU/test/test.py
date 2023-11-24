import requests
import base64
import json

def main():
    with open("cat.jpg", "rb") as fp:
        base64_str = base64.b64encode(fp.read()).decode()
    prompts = "cat,dog,frog,mouse"
    data = {
        "image": base64_str,
        "prompt": prompts
    }

    response = requests.post("http://127.0.0.1:9001/2015-03-31/functions/function/invocations", 
                             data=json.dumps(data))
    probs = json.loads(response.text)
    print(probs)

if __name__ == "__main__":
    main()
