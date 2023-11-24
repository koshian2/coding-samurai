import boto3
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile_name", type=str, default="default", help="profile name for aws credentials")
    parser.add_argument("--lambda_name", type=str, required=True, help="lambda function name")
    parser.add_argument("--role", type=str, required=True, help="lambda execution role")
    parser.add_argument("--image_uri", type=str, required=True, help="ECR image uri to use function")
    parser.add_argument("--memory_size", type=int, default=512, help="memory size for lambda function")
    parser.add_argument("--timeout", type=int, default=3, help="timeout for lambda function")

    args = parser.parse_args()
    return args

def main(args: argparse.Namespace):
    boto_session = boto3.Session(profile_name=args.profile_name)
    lambda_client = boto_session.client("lambda")
    print("Creating Lambda function...")
    create_lambda_response = lambda_client.create_function(
        FunctionName=args.lambda_name,
        PackageType="Image",
        Code={
            "ImageUri": args.image_uri,
        },
        Role=args.role,
        MemorySize=args.memory_size,
        Timeout=args.timeout,
    )
    print(create_lambda_response)
    
if __name__ == "__main__":
    args = parse_args()
    main(args)

