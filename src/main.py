#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, S3Backend
from cdktf_cdktf_provider_aws.provider import AwsProvider

from src.dynamo import DynamoDB
from src.api import RESTApi
from src.timestream import Timestream


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

        dynamo = DynamoDB(self, "dynamo", isstream=True, tags=tags)

        api = RESTApi(
            self,
            "api",
            endpoint_name="sensordata",
            table_name=dynamo.table_name,
            put_policies_arn=[dynamo.crud_arn],
            get_policies_arn=[dynamo.crud_arn],
            put_file_path="/root/unsw/FAIC-Project-AWS-Template/src/code/archived/table_put.zip",
            get_file_path="/root/unsw/FAIC-Project-AWS-Template/src/code/archived/table_get.zip",
            tags=tags,
        )

        Timestream(self, "ts", "test", tags=tags)


app = App()
MyStack(app, "brewai-sensor-iaq", "dev", "Alan")

app.synth()
