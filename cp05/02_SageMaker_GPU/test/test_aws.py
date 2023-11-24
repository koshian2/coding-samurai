import boto3
import uuid
import time
import io
import datetime
import json
from typing import Any

def run_inference(video_path: str,
                  s3_bucket_name: str="async-outputs",
                  endpoint_name: str="EdoFlowRaft",
                  input_key: str="edoflow/input"):
    # Get boto session
    boto_session = boto3.Session(profile_name="develop")
    # Upload input to S3
    s3_client = boto_session.client("s3")
    input_file_key = f"{input_key}/{uuid.uuid4()}"
    s3_client.upload_file(video_path, s3_bucket_name, input_file_key)

    # Inference
    sagemaker_runtime_client = boto_session.client("sagemaker-runtime")
    response = sagemaker_runtime_client.invoke_endpoint_async(
        EndpointName=endpoint_name,
        ContentType="binary/octet-stream",
        InputLocation=f"s3://{s3_bucket_name}/{input_file_key}"
    )
    print("Async inference response")
    print(response)

    # Check result : polling with exponential backoff
    success_file_key = response["OutputLocation"].replace(f"s3://{s3_bucket_name}/", "")
    failure_file_key = response["FailureLocation"].replace(f"s3://{s3_bucket_name}/", "")

    # polling
    return exponential_polling(s3_client, success_file_key, failure_file_key)

def exponential_polling(s3_client: Any,
                        success_file_key: str, 
                        failure_file_key: str,
                        s3_bucket_name: str="async-outputs"):
    waiting_time = 3
    backoff_ratio = 1.3

    start_time = time.time()

    while True:
        if time.time() - start_time > 3600:
            break

        # is success / failure exists ?
        s3_success_result = s3_client.list_objects(Bucket=s3_bucket_name, Prefix=success_file_key)
        s3_failure_result = s3_client.list_objects(Bucket=s3_bucket_name, Prefix=failure_file_key)

        # Download (Success)
        if "Contents" in s3_success_result.keys():
            print(datetime.datetime.now(), "Success")
            with io.BytesIO() as buf:
                s3_client.download_fileobj(s3_bucket_name, success_file_key, buf)
                buf.seek(0)
                content = buf.getvalue()
                result = json.loads(content)
            return result
        # Download (Failure)
        elif "Contents" in s3_failure_result.keys():
            print(datetime.datetime.now(), "Failure")
            with io.BytesIO() as buf:
                s3_client.download_fileobj(s3_bucket_name, failure_file_key, buf)
                buf.seek(0)
                result = buf.getvalue()
            return result
        else:
            print(datetime.datetime.now(), "Processing")
            time.sleep(waiting_time)
            waiting_time *= backoff_ratio

    return "timeout"

if __name__ == "__main__":
    result = run_inference("暴れん坊将軍のテーマ [nBXX-RT38uQ].mp4")
    print(result)