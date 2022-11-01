import hashlib
import json
from constructs import Construct
from cdktf import TerraformOutput
from cdktf_cdktf_provider_aws.iam_policy import IamPolicy
from cdktf_cdktf_provider_aws.iam_role import IamRole
from cdktf_cdktf_provider_aws.data_aws_iam_policy_document import (
    DataAwsIamPolicyDocument,
)
from cdktf_cdktf_provider_aws.api_gateway_rest_api import ApiGatewayRestApi
from cdktf_cdktf_provider_aws.api_gateway_resource import ApiGatewayResource
from cdktf_cdktf_provider_aws.api_gateway_method import ApiGatewayMethod
from cdktf_cdktf_provider_aws.api_gateway_stage import ApiGatewayStage
from cdktf_cdktf_provider_aws.api_gateway_deployment import ApiGatewayDeployment
from cdktf_cdktf_provider_aws.api_gateway_integration import ApiGatewayIntegration
from cdktf_cdktf_provider_aws.api_gateway_usage_plan import ApiGatewayUsagePlan
from cdktf_cdktf_provider_aws.api_gateway_api_key import ApiGatewayApiKey
from cdktf_cdktf_provider_aws.api_gateway_usage_plan_key import ApiGatewayUsagePlanKey
from cdktf_cdktf_provider_aws.lambda_function import LambdaFunction
from cdktf_cdktf_provider_aws.lambda_permission import LambdaPermission
from cdktf_cdktf_provider_aws.cloudwatch_log_group import CloudwatchLogGroup


class RESTApi(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        endpoint_name: str,
        table_name: str,
        put_policies_arn: list,
        get_policies_arn: list,
        put_file_path: str,
        get_file_path: str,
        tags: dict,
    ):

        super().__init__(scope, id)

        rest_api = ApiGatewayRestApi(
            self,
            "rest-api",
            name=f'ProjectRestApi-{tags["project"]}-{tags["env"]}',
            api_key_source="HEADER",
            endpoint_configuration={"types": ["REGIONAL"]},
            tags=tags,
        )

        resource = ApiGatewayResource(
            self,
            "resource",
            path_part=endpoint_name,
            rest_api_id=rest_api.id,
            parent_id=rest_api.root_resource_id,
        )

        assume = DataAwsIamPolicyDocument(
            self,
            "assume",
            statement=[
                {
                    "actions": ["sts:AssumeRole"],
                    "principals": [
                        {
                            "type": "Service",
                            "identifiers": ["lambda.amazonaws.com"],
                        }
                    ],
                }
            ],
        )

        put_lambdas_role = IamRole(
            self,
            "put_lambda_role",
            name=f"Lambda-PUT-{tags['project']}-{tags['env']}",
            assume_role_policy=assume.json,
            managed_policy_arns=[
                "arn:aws:iam::092201464628:policy/LambdaLogging",
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
            ]
            + put_policies_arn,
            tags=tags,
        )

        """ h = hashlib.sha1()
        with open(put_file_path) as file:
            chunk = 0
            while chunk != b"":
                chunk = file.read(1024)
                h.update(chunk) """

        put_function = LambdaFunction(
            self,
            "lambda_put",
            filename=put_file_path,
            function_name=f"PUTTable-{tags['project']}-{tags['env']}",
            # source_code_hash=h.hexdigest(),
            role=put_lambdas_role.arn,
            handler=f"{put_file_path.split('/')[-1].split('.')[0]}.handler",
            runtime="python3.9",
            memory_size=128,
            timeout=5,
            environment={
                "variables": {
                    "REGION": "ap-southeast-2",
                    "DYNAMO_TABLE": table_name,
                }
            },
            tags=tags,
        )

        permission = LambdaPermission(
            self,
            "put_permission",
            statement_id="AllowExecutionFromAPIGateway",
            action="lambda:InvokeFunction",
            function_name=put_function.function_name,
            principal="apigateway.amazonaws.com",
            source_arn="arn:aws:execute-api:ap-southeast-2:092201464628:*/*/*",
        )

        put_logs = CloudwatchLogGroup(
            self,
            "putlog",
            name=f"/aws/lambda/{put_function.function_name}",
            retention_in_days=30,
            tags=tags,
        )

        put_methode = ApiGatewayMethod(
            self,
            "put_rest",
            rest_api_id=rest_api.id,
            resource_id=resource.id,
            http_method="PUT",
            authorization="NONE",
            api_key_required=True,
        )

        put_integration = ApiGatewayIntegration(
            self,
            "put_integration",
            rest_api_id=rest_api.id,
            resource_id=resource.id,
            http_method="PUT",
            integration_http_method="POST",
            type="AWS_PROXY",
            uri=put_function.invoke_arn,
        )

        # GET
        get_lambdas_role = IamRole(
            self,
            "get_lambda_role",
            name=f"Lambda-GET-{tags['project']}-{tags['env']}",
            assume_role_policy=assume.json,
            managed_policy_arns=[
                "arn:aws:iam::092201464628:policy/LambdaLogging",
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
            ]
            + get_policies_arn,
            tags=tags,
        )

        """ hg = hashlib.sha1()
        with open(get_file_path) as file:
            chunk = 0
            while chunk != b"":
                chunk = file.read(1024)
                hg.update(chunk) """

        get_function = LambdaFunction(
            self,
            "lambda_get",
            filename=get_file_path,
            function_name=f"GETTable-{tags['project']}-{tags['env']}",
            # source_code_hash=h.hexdigest(),
            role=get_lambdas_role.arn,
            handler=f"{get_file_path.split('/')[-1].split('.')[0]}.handler",
            runtime="python3.9",
            memory_size=128,
            timeout=5,
            environment={
                "variables": {
                    "REGION": "ap-southeast-2",
                    "DYNAMO_TABLE": table_name,
                }
            },
            tags=tags,
        )

        LambdaPermission(
            self,
            "get_permission",
            statement_id="AllowExecutionFromAPIGateway",
            action="lambda:InvokeFunction",
            function_name=get_function.function_name,
            principal="apigateway.amazonaws.com",
            source_arn="arn:aws:execute-api:ap-southeast-2:092201464628:*/*/*",
        )

        CloudwatchLogGroup(
            self,
            "getlog",
            name=f"/aws/lambda/{get_function.function_name}",
            retention_in_days=30,
            tags=tags,
        )

        get_methode = ApiGatewayMethod(
            self,
            "get_rest",
            rest_api_id=rest_api.id,
            resource_id=resource.id,
            http_method="GET",
            authorization="NONE",
            api_key_required=True,
        )

        get_integration = ApiGatewayIntegration(
            self,
            "get_integration",
            rest_api_id=rest_api.id,
            resource_id=resource.id,
            http_method="GET",
            integration_http_method="POST",
            type="AWS_PROXY",
            uri=get_function.invoke_arn,
        )

        deployement = ApiGatewayDeployment(
            self,
            "rest-deploy",
            rest_api_id=rest_api.id,
            lifecycle={"create_before_destroy": True},
            triggers={"redeployment": "1"},
            depends_on=[put_integration, get_integration],
        )

        rest_stage = ApiGatewayStage(
            self,
            "rest_stage",
            deployment_id=deployement.id,
            rest_api_id=rest_api.id,
            stage_name="v1",
            tags=tags,
        )

        plan = ApiGatewayUsagePlan(
            self,
            "plan",
            name=f"RestApi-{tags['project']}-{tags['env']}",
            api_stages=[{"apiId": rest_api.id, "stage": rest_stage.stage_name}],
            tags=tags,
        )

        key = ApiGatewayApiKey(
            self, "key", name=f"REST-KEY-{tags['project']}-{tags['env']}", tags=tags
        )

        ApiGatewayUsagePlanKey(
            self, "usagekey", key_id=key.id, key_type="API_KEY", usage_plan_id=plan.id
        )

        TerraformOutput(self, "rest_api_url", value=rest_stage.invoke_url)
        TerraformOutput(self, "rest_api_key_name", value=key.name)
        TerraformOutput(self, "rest_api_key_value", value=key.value, sensitive=True)
