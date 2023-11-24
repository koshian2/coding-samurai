from yt_dlp import YoutubeDL

def download_youtube(url): 
    ydl_opts = {
        "format": "best",
        "paths": {
            "home": "video"
        }
    }
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([url])

if __name__ == '__main__':
    download_youtube('https://www.youtube.com/watch?v=nBXX-RT38uQ')