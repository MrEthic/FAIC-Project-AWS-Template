#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, S3Backend
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.iam_role import IamRole
from cdktf_cdktf_provider_aws.data_aws_iam_policy_document import (
    DataAwsIamPolicyDocument,
)
from cdktf_cdktf_provider_aws.lambda_function import LambdaFunction

from src.dynamo import DynamoDB
from src.api import RESTApi
from src.timestream import Timestream
from src.scheduled_lambdas import ScheduledLambdas


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str, env: str, project_owner: str):
        super().__init__(scope, ns)

        tags = {"env": env, "project": ns, "project_owner": project_owner}

        AwsProvider(self, "AWS", region="ap-southeast-2")

        # Backend for storing state
        S3Backend(
            self,
            bucket="terraform-backend-faic-infra",
            key=f"{ns}/terraform-{env}.tfstate",
            region="ap-southeast-2",
        )

        # dynamo = DynamoDB(self, "dynamo", isstream=False, tags=tags)

        t = Timestream(self, "ts", "brewai_api", tags=tags)

        api = RESTApi(
            self,
            "api",
            endpoint_name="sensordata",
            tags=tags,
        )

        api.add_endpoint(
            http="PUT",
            policies=[t.crud_arn],
            filename="/root/unsw/FAIC-Project-AWS-Template/src/code/archived/timestream_put.zip",
            environement={"DATABASE_NAME": t.db_name, "TABLE_NAME": t.table_name},
        )

        api.finalize()

        ScheduledLambdas(
            self,
            "fetcher",
            "FetchBrewAI",
            "rate(1 minute)",
            "/root/unsw/FAIC-Project-AWS-Template/src/code/archived/brewai_fetch_githide.zip",
            [],
            512,
            20,
            {},
            tags,
        )


app = App()
MyStack(app, "brewai-sensor-iaq", "dev", "Alan")

app.synth()
