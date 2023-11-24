import boto3
import sagemaker
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile_name", type=str, default="default", help="profile name for aws credentials")
    parser.add_argument("--endpoint_name", type=str, required=True, help="endpoint name for sagemaker async inference")
    parser.add_argument("--role", type=str, required=True, help="role for sagemaker")
    parser.add_argument("--image_uri", type=str, required=True, help="ECR image uri to use an endpoint")
    parser.add_argument("--instance_type", type=str, required=True, help="instance type of an endpoint")
    parser.add_argument("--s3_output_path", type=str, required=True, help="S3 uri for success case")
    parser.add_argument("--s3_failure_path", type=str, required=True, help="S3 uri for failure case")
    parser.add_argument("--disable_auto_scaling", action="store_true", help="auto scaling disable flag (default: autoscaling on)")
    parser.add_argument("--autoscaling_up_threshold_seconds", type=int, default=60, help="num seconds until instance is up")
    parser.add_argument("--autoscaling_down_threshold_seconds", type=int, default=1200, help="num seconds until instance is down")

    args = parser.parse_args()
    return args

def deploy_model(args: argparse.Namespace):
    ## session, role
    boto_session = boto3.Session(profile_name=args.profile_name)
    sagemaker_session = sagemaker.Session(boto_session=boto_session)

    # Create a sagemaker model
    print("Creating a model ...")
    model_response = sagemaker_session.create_model(
        name=args.endpoint_name, 
        role=args.role,
        container_defs={
            "Image": args.image_uri
        })

    # Create a endpoint config
    print("Creating an endpoint ...")
    endpoint_config_response = sagemaker_session.endpoint_from_production_variants(
        name=args.endpoint_name,
        production_variants=[
            {
                "VariantName": "variant1",
                "ModelName": args.endpoint_name,
                "InstanceType": args.instance_type,
                "InitialInstanceCount": 1
            }
        ],
        async_inference_config_dict={
            "OutputConfig": {
                "S3OutputPath": args.s3_output_path,
                "S3FailurePath": args.s3_failure_path
            }
        }
    )

    # Apply auto scaling
    if not args.disable_auto_scaling:
        # Get Autoscaling client
        autoscaling_client = boto_session.client("application-autoscaling")
        # Get Cloudwatch client
        cloudwatch_client = boto_session.client("cloudwatch")

        # Register scalable target
        print("Register scalable target")
        resource_id = f"endpoint/{args.endpoint_name}/variant/variant1"
        register_scalable_target_response = autoscaling_client.register_scalable_target(
            ServiceNamespace='sagemaker', 
            ResourceId=resource_id,
            ScalableDimension='sagemaker:variant:DesiredInstanceCount',
            MinCapacity=0,  
            MaxCapacity=1
        )
        print(register_scalable_target_response)

        # Put scaling policy
        print("Put scaling policy")
        put_scaling_policy_response = autoscaling_client.put_scaling_policy(
            PolicyName='Invocations-ScalingPolicy',
            ServiceNamespace='sagemaker', 
            ResourceId=resource_id, 
            ScalableDimension='sagemaker:variant:DesiredInstanceCount',
            PolicyType='TargetTrackingScaling',
            TargetTrackingScalingPolicyConfiguration={
                'TargetValue': 0.9, 
                'CustomizedMetricSpecification': {
                    'MetricName': 'ApproximateBacklogSizePerInstance',
                    'Namespace': 'AWS/SageMaker',
                    'Dimensions': [
                        {'Name': 'EndpointName', 'Value': args.endpoint_name }
                    ],
                    'Statistic': 'Maximum',
                },
                'ScaleInCooldown': 900,
                'ScaleOutCooldown': 180
            }
        )
        print(put_scaling_policy_response)

        # Calculate periods and evaluation periods
        periods, evaluation_periods = [], []
        for val in [args.autoscaling_up_threshold_seconds, args.autoscaling_down_threshold_seconds]:
            if val <= 600:
                periods.append(60) # 1min
                evaluation_periods.append(val // 60)
            elif val <= 3000:
                periods.append(300) # 5min
                evaluation_periods.append(val // 300)
            else:
                periods.append(1800) # 10min
                evaluation_periods.append(min(val // 1800, 10))

        # Update autoscaling metrics
        for i, alarm in enumerate(cloudwatch_client.describe_alarms(AlarmNames=[x["AlarmName"] for x in put_scaling_policy_response["Alarms"]])["MetricAlarms"]):
            put_alarm_response = cloudwatch_client.put_metric_alarm(
                AlarmName=alarm["AlarmName"],
                AlarmDescription=alarm["AlarmDescription"],
                ActionsEnabled=alarm["ActionsEnabled"],
                OKActions=alarm["OKActions"],
                AlarmActions=alarm["AlarmActions"],
                InsufficientDataActions=alarm["InsufficientDataActions"],
                MetricName=alarm["MetricName"],
                Namespace=alarm["Namespace"],
                Statistic=alarm["Statistic"],
                Dimensions=alarm["Dimensions"],
                Period=periods[i],
                EvaluationPeriods=evaluation_periods[i],
                Threshold=alarm["Threshold"],
                ComparisonOperator=alarm["ComparisonOperator"])
            print(put_alarm_response)

if __name__ == "__main__":
    args = parse_args()
    deploy_model(args)
