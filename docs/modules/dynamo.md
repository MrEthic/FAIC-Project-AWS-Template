# DynamoDB Table

Use this module to create a dynamo table for the project.

## dynamo.DynamoDB
Class for the DynamoDB Table.

**Terraform resources:**

1. DynamodbTable: The Dynamo Table.
2. IamPolicy: A policy that allows all CRUD opperation on the table.

If isstream is set to true, it will enable DynamoStream and attach a websocket api on the stream.

**Terraform resources for stream:**

1. IamPolicy: A policy to allow stream reading.
2. [DynamoWebsocket](dynamo.md#streamingdynamowebsocket): The websocket api.

***Arguments***

| Name | Type | Description |
| ------------ | ------------- | ------------ |
| isstream | bool | Enable or not the dynamo stream |
| tags | dict  | Tags for all resource, must include a 'project' and 'env' key |

***Attributes***

| Name | Type | Description |
| ------------ | ------------- | ------------ |
| table_name | str | Name of the dynamo table |
| crud_arn | str | ARN of the CRUD policy |

## streaming.DynamoWebsocket
Resources for websocket API associated to a dynamo table.

**Terraform resources:**

1. DynamodbTable: The table for managing open connections.
2. IamPolicy: Policy for managing connections.
3. Apigatewayv2Api: The Websocket API.
4. IamRole: Role for lambdas.
5. LambdaFunction: Manager and Messager for the API.
6. LambdaPermission: Allow execution from api.
7. CloudwatchLogGroup: Logs for lambdas.
8. Apigatewayv2Integration: API Integration.
9. Apigatewayv2Route: connect and disconnect routes.
10. Apigatewayv2Deployment: API deployement.
11. Apigatewayv2Stage: API version.
12. LambdaEventSourceMapping: Connect lambdas to stream.

| Argument | Type | Description |
| ------------ | ------------- | ------------ |
| stream_arn | str  | The dynamo stream arn |
| stream_policy_arn | str | The arn to allow readings of the stream |
| tags | dict | Tags for all resource, must include a 'project' and 'env' key |

## Example

Create a dynamo table with no streams:
```python
from src.dynamo import DynamoDB

tags = {
    "project": "My Project",
    "env": "dev"
}

dynamo = DynamoDB(self, "dynamo", isstream=False, tags=tags)
```