import boto3
import uuid
import time
import io
import json
import requests

def run_inference(video_path: str,
                  s3_bucket_name: str="async-outputs",
                  endpoint_name: str="EdoFlowRaft",
                  input_key: str="edoflow/input"):
    # Get boto session
    boto_session = boto3.Session()
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

    # Check result : polling with exponential backoff
    success_file_key = response["OutputLocation"].replace(f"s3://{s3_bucket_name}/", "")
    failure_file_key = response["FailureLocation"].replace(f"s3://{s3_bucket_name}/", "")

    # polling
    return exponential_polling(success_file_key, failure_file_key, input_file_key)

def run_video_clip(output_file: str,
                   input_key: str,
                   start_seconds: int,
                   end_seconds: int,
                   bucket_name: str = "async-outputs"):
    boto_session = boto3.Session()
    lambda_client = boto_session.client("lambda")
    payload = {
        "bucket": bucket_name,
        "input_key": input_key,
        "start_seconds": start_seconds,
        "end_seconds": end_seconds,
        "output_key": f"edoflow/output/{uuid.uuid4()}"
    }
    response = lambda_client.invoke(FunctionName="EdoFlowCutVideo",
                                    Payload=json.dumps(payload).encode("utf-8"))
    response = response["Payload"].read().decode()

    s3_client = boto_session.client("s3")
    s3_client.download_file(bucket_name, payload["output_key"], output_file)
    return output_file

def run_video_clip_locally(file_to_upload: str,
                           input_prefix: str,
                           output_file: str,
                           start_seconds: int,
                           end_seconds: int,
                           upload_bucket: str = "async-outputs"):
    # upload video
    boto_session = boto3.Session()
    s3_client = boto_session.client("s3")
    input_file_key = f"{input_prefix}/{uuid.uuid4()}"
    s3_client.upload_file(file_to_upload, upload_bucket, input_file_key)
    # request
    payload = {
        "bucket": upload_bucket,
        "input_key": input_file_key,
        "start_seconds": start_seconds,
        "end_seconds": end_seconds,
        "output_key": f"edoflow/output/{uuid.uuid4()}"
    }
    response = requests.post("http://host.docker.internal:9012/2015-03-31/functions/function/invocations", 
                             data=json.dumps(payload).encode("utf-8"))
    # download result
    s3_client.download_file(payload["bucket"], payload["output_key"], output_file)
    return output_file

def exponential_polling(success_file_key: str, 
                        failure_file_key: str,
                        input_file_key: str,
                        s3_bucket_name: str="async-outputs"):
    boto_session = boto3.Session()
    s3_client = boto_session.client("s3")
    waiting_time = 3
    backoff_ratio = 1.3

    result = {
        "success_file_key": success_file_key,
        "failure_file_key": failure_file_key,
        "input_file_key": input_file_key
    }
    start_time = time.time()

    while True:
        if time.time() - start_time > 60:
            break

        # is success / failure exists ?
        s3_success_result = s3_client.list_objects(Bucket=s3_bucket_name, Prefix=success_file_key)
        s3_failure_result = s3_client.list_objects(Bucket=s3_bucket_name, Prefix=failure_file_key)

        # Download (Success)
        if "Contents" in s3_success_result.keys():
            with io.BytesIO() as buf:
                s3_client.download_fileobj(s3_bucket_name, success_file_key, buf)
                buf.seek(0)
                content = buf.getvalue()
                content = json.loads(content)
                result["status"] = "success"
                result["content"] = content
            return result
        # Download (Failure)
        elif "Contents" in s3_failure_result.keys():
            with io.BytesIO() as buf:
                s3_client.download_fileobj(s3_bucket_name, failure_file_key, buf)
                buf.seek(0)
                content = buf.getvalue()
                result["status"] = "failure"
                result["content"] = content
            return result
        else:
            time.sleep(waiting_time)
            waiting_time *= backoff_ratio

    result["status"] = "timeout"
    result["content"] = "Now Processing"
    return result