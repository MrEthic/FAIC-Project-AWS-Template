# API Gateway

Use this module to build an API Gateway for the project.

## api.RESTApi
Class for the API Gateway.

**Terraform resources:**

1. ApiGatewayRestApi: The REST API.
2. ApiGatewayResource: API resource for the project (/endpoint_name).
3. ApiGatewayResource: /predictions resource.

***Arguments***

| Name | Type | Description |
| ------------ | ------------- | ------------ |
| endpoint_name | str | Name of the resource for the project api |
| tags | dict | Tags for all resource, must include a 'project' and 'env' key |

***Attributes***

| Name | Type | Description |
| ------------ | ------------- | ------------ |
| integrations | list | List of integration on the api |
| api_id | str | Unique id provided by AWS |
| data_resource_id | str | Id of the user defined resource |
| pred_resource_id | str | Id of the predictions resource |
| dim_resource_id | str | Id of the dimension resource |
| api_key_value | str | API key secret value set during finalize() |

## api.RESTApi.add_endpoint
Methode to attach Lambda endpoint to the API.

**Terraform resources:**

1. IamRole: Role for the Lambda.
2. LambdaFunction: The Lambda function.
3. CloudwatchLogGroup: Log group for Lambda Logging (retention 30 days).
4. LambdaPermission: Allow invokation of the lambda from API Gateway.
5. ApiGatewayMethod: Create a method (GET, PUT, etc.) on the endpoint.
6. ApiGatewayIntegration: Attach the Lambda to the method.

| Argument | Type | Description |
| ------------ | ------------- | ------------ |
| http | str | Http methode (GET, PUT, DELETE, etc.) |
| policies | list | List of policies arn to attatch to the function |
| filename | str | Path to the zip file of the lambda |
| environement | dict | Environement variables to pass to the function |
| timeout | int | Lambda timeout. Default 5, must be lower than 30 |
| resource | str | data, pred or dim for the resource to attatch the endpoint to. |

**Returns: The function arn.**

## api.RESTApi.finalize
Methode to finalize the API. 

**Terraform resources:**

1. ApiGatewayDeployment: Deploy the API (make it accessible to the public internet).
2. ApiGatewayStage: An API Stage (version) with name 'v1'.
3. ApiGatewayUsagePlan: A usage plan for the api. No restriction applied on it.
4. ApiGatewayApiKey: An API Key to query the endpoints.
5. ApiGatewayUsagePlanKey: Attach the key to the usage plan.

## Example

Create an api and attach one lambda to /stockprice/GET:
```python
from src.api import RESTApi

tags = {
    "project": "My Project",
    "env": "dev"
}

myapi = RESTApi(
    self,
    "api",
    endpoint_name="stockprice",
    tags=tags,
)

myapi.add_endpoint(
    http="GET",
    policies=[database.crud_policy_arn],
    filename="path/to/my/zipfile.zip",
    environement={"DATABASE_NAME": "db", "TABLE_NAME": "stockprice"},
    timeout=20,
)

api.finalize()
```