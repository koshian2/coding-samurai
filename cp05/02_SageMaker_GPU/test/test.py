import requests
import json

def main():
    with open("暴れん坊将軍のテーマ [nBXX-RT38uQ].mp4", "rb") as fp:
        binary = fp.read()

    response = requests.post("http://127.0.0.1:9011/invocations", 
                             data=binary)
    result = json.loads(response.text)
    print(result)

if __name__ == "__main__":
    main()
