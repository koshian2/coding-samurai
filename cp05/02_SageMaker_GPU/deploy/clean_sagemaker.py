import boto3
import sagemaker
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile_name", type=str, default="default", help="profile name for aws credentials")
    parser.add_argument("--endpoint_name", type=str, required=True, help="endpoint name for sagemaker async inference")
    parser.add_argument("--no_auto_scaling", action="store_true", help="True if the endpoint has no autoscaling (default: autoscaling on)")

    args = parser.parse_args()
    return args

def clean_up_resources(args: argparse.Namespace):
    message = [
        "This function will erases all resources for the endpoint. Are you sure? "
        "",
        f"    Endpoint name : {args.endpoint_name} "
        ""
        "Type 'delete all' if you really want to process.\n"
    ]

    boto3_session = boto3.Session(profile_name=args.profile_name)
    sagemaker_session = sagemaker.Session(boto_session=boto3_session)

    if input("\n".join(message)) == "delete all":
        autoscaling_client = boto3_session.client("application-autoscaling", region_name="ap-northeast-1")
        resource_id = f"endpoint/{args.endpoint_name}/variant/variant1"

        # Remove scalable target
        if args.no_auto_scaling:
            print("Deregister scalable target")
            response = autoscaling_client.deregister_scalable_target(
                ServiceNamespace="sagemaker",
                ResourceId=resource_id,
                ScalableDimension="sagemaker:variant:DesiredInstanceCount",
            )
            print(response)

        # Remove endpoint
        print("Delete endpoint")
        response =  sagemaker_session.sagemaker_client.delete_endpoint(EndpointName=args.endpoint_name)
        print(response)

        # Remove endpoint config
        print("Delete endpoint config")
        response = sagemaker_session.sagemaker_client.delete_endpoint_config(EndpointConfigName=args.endpoint_name)
        print(response)

        # Remove model
        print("Delete model")
        response = sagemaker_session.sagemaker_client.delete_model(ModelName=args.endpoint_name)
        print(response)
    else:
        print("aborted")

if __name__ == "__main__":
    args = parse_args()
    clean_up_resources(args)
    print("Done.")

