import moviepy.editor as mpe
import boto3
import tempfile

def lambda_handler(event, context):
    boto_session = boto3.Session()
    s3_client = boto_session.client('s3')

    with tempfile.NamedTemporaryFile() as orig_video, tempfile.NamedTemporaryFile(suffix=".mp4") as out_video:
        s3_client.download_file(event["bucket"], event["input_key"], orig_video.name)
        orig_video.flush()
        videoclip = mpe.VideoFileClip(orig_video.name)
        subclip = videoclip.subclip(event["start_seconds"], min(event["end_seconds"], videoclip.duration))
        subclip.write_videofile(out_video.name, temp_audiofile_path="/tmp")
        s3_client.upload_file(out_video.name, event["bucket"], event["output_key"])

    return {"status_code": 200}