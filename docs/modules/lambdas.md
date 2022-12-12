# Lambdas

Use this module to create lambdas for the project.

## lambdas.ScheduledLambdas
A lambda function scheduled by event bridge.

**Terraform resources:**

1. IamRole: Role for the lambda.
2. LambdaFunction; The lambda function.
3. CloudwatchLogGroup: Log group for logging.
4. CloudwatchEventRule: Schedule event rule.
5. CloudwatchEventTarget: Attach event rule to the function.
6. LambdaPermission; Allow invokation of the function from CloudWhatch.

***Arguments***

| Name | Type | Description |
| ------------ | ------------- | ------------ |
| name | str | Name of the lambda function |
| schedule_expression | str | A valid scheduled expression, ex: 'rate(1 hour)' |
| filename | str | Path to the zipfile containing lambda code |
| policies | list | List of policies arn to attach to the function |
| memory_size | int | Lambda memory size in MB |
| timeout | int | Timeout of the function |
| environement | dict | Environement variable to pass to the function |
| tags | dict  | Tags for all resource, must include a 'project' and 'env' key |

## lambdas.InvokableLambdas
A lambda function usable by other services.

**Terraform resources:**

1. IamRole: Role for the lambda.
2. LambdaFunction; The lambda function.
3. CloudwatchLogGroup: Log group for logging.
4. LambdaPermission; Allow invokation of the function from the consumer.

***Arguments***

| Name | Type | Description |
| ------------ | ------------- | ------------ |
| name | str | Name of the lambda function |
| filename | str | Path to the zipfile containing lambda code |
| policies | list | List of policies arn to attach to the function |
| invoke_principal | str | Principal of the consumer of the lambda (lambda.amazonaws.com, ec2.amazonaws.com, etc.) |
| invoke_from_arn | str | ARN of the consumer(s) |
| memory_size | int | Lambda memory size in MB |
| timeout | int | Timeout of the function |
| environement | dict | Environement variable to pass to the function |
| tags | dict  | Tags for all resource, must include a 'project' and 'env' key |

## Example

Create a schudled lambda that runs every minute:
```python
from src.lambdas import ScheduledLambdas

tags = {
    "project": "My Project",
    "env": "dev"
}

ScheduledLambdas(
    self,
    "lambda",
    name="do-something-every-minute",
    schedule_expression="rate(1 minute)",
    filename="path/to/my/zipfile.zip",
    policies=[read_my_db_policy_arn],
    memory_size=512,
    timeout=20,
    environement={},
    tags=tags,
)
```

Create a lambda that can be invoke in any lambda:
```python
from src.lambdas import InvokableLambdas

InvokableLambdas(
    self,
    "lambda",
    name="usefull-lambda",
    filename="path/to/my/zipfile.zip",
    policies=[],
    invoke_principal="lambda.amazonaws.com",
    invoke_from_arn="arn:aws:lambda:region:account-id:function:*",
    memory_size=512,
    timeout=20,
    environement={},
    tags=tags,
)
```