#!/usr/bin/env python
import json
import os
from dotenv import load_dotenv
from constructs import Construct
from cdktf import App, TerraformStack, S3Backend
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.iam_policy import IamPolicy
from cdktf_cdktf_provider_aws.iam_role import IamRole
from cdktf_cdktf_provider_aws.data_aws_iam_policy_document import (
    DataAwsIamPolicyDocument,
)
from cdktf_cdktf_provider_aws.lambda_function import LambdaFunction
from cdktf_cdktf_provider_aws.lambda_permission import LambdaPermission
from cdktf_cdktf_provider_aws.cloudwatch_log_group import CloudwatchLogGroup

from src.dynamo import DynamoDB
from src.api import RESTApi
from src.timestream import Timestream
from src.lambdas import ScheduledLambdas, InvokableLambdas

load_dotenv()


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str, env: str, project_owner: str):
        super().__init__(scope, ns)

        tags = {"env": env, "project": ns, "project_owner": project_owner}

        AwsProvider(self, "AWS", region="ap-southeast-2", profile="unsw")

        # Backend for storing state
        S3Backend(
            self,
            bucket="terraform-backend-faic-infra",
            key=f"{ns}/terraform-{env}.tfstate",
            region="ap-southeast-2",
        )


app = App()
MyStack(app, "mysatck", "dev", "me")

app.synth()
