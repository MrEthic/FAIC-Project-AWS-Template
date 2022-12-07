# Boto3
Boto3 is used to interact with resources on aws. It can be used to query data from databases, read logs, and even create resources. Boto3 is a wrapper that uses aws REST API.

## Getting started
First, you will need to install boto3 in your environement. Note that boto3 is natively available on lambda runtime.
On your local machine, run `pip install boto3` or `conda install boto3`.

Boto3 is very well documented online, simply search "boto3 *what you wan't to do*" on google and you will find documentation.

## Session and credentials
A boto3 Session is used to authenticate you. You can create a session using `boto3.Session()`. Boto3 will use default configuration to open the Session. It is a good practice to explicitly specify the region you want to intrect with in the Session: `boto3.Session(region_name='ap-southeast-3')`.

## Boto3 in Lambdas
Boto3 will inherite the lambda permission.

## Boto3 in local
Refere to the [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) for detailed explanation on boto3 credentials.

The best practice would be to install the [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) on you local machine and then configure profiles, access key and secret key id on the `~/./aws directory`.

However, you can still specify your AWS access when opening a session:
```python
session = session.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)
```

***Extract from boto3 docs:***

ACCESS_KEY, SECRET_KEY, and SESSION_TOKEN are variables that contain your access key, secret key, and optional session token. Note that the examples above do not have hard coded credentials. **We do not recommend hard coding credentials in your source code**.

## Clients
Boto3 clients are used to interact with specific AWS API, their is a lot of different client. To create one simply use:

```python
session = boto3.Session(region_name='ap-southeast-3')

dynamodb_client = session.client("dynamodb")
timestreamwrite_client = session.client("timestream-write")
lambda_client = session.client("lambda")
...
```

## DynamoDB Examples
Assuming you have a working boto3 client.

### Put item
Insert an item in a dynamo table.
```python
import boto3

session = boto3.Session(region_name='ap-southeast-3')
dynamodb_client = session.client("dynamodb")

dynamodb_response = dynamodb_client.put_item(
    TableName="TABLE_NAME",
    Item={
        "Key1": {"S": "Hello"},
        "Key2": {"N": "2.154864584"},
        "Key3": {"L": ["1", "2", "3"]},
    },
)
```

### Query items
Query (different from scaning) items in dynamodb. You can use boto3 resource to abstract some of the parsing logic.

```python
import boto3

dynamodb = boto3.resource("dynamodb", region_name='ap-southeast-3')
table = dynamodb.Table("TABLE_NAME")

dynamodb_response = table.query(
    KeyConditionExpression=Key("Key").eq("somethin")
    & Key("Timestamp").between(1, 60),
)
```

**Boto3 dom't use float but Decimals.** You may wan't to build a Encoder for this.

```python
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

query_result = json.dumps(dynamodb_response, cls=DecimalEncoder)
```

## Timestream
There is two timestream client, `timestream-write` and `timestream-query`.

### Query a table
Execute a SQL query and parse the results.
```python
import boto3
import pandas

session = boto3.Session(region_name="ap-southeast-2")
ts_query = session.client("timestream-query")

QUERY_1 = """
SELECT 
  time,
  deviceId,
  measure_value::double AS temperature
FROM "ProjectTable-brewai-sensor-iaq-dev"."brewai_api"
WHERE
  measure_name='temperature'
  AND time between ago(1h) and now()
ORDER BY time DESC
"""

response = ts_query.query(
    QueryString=QUERY_1
)

columns_name = [col['Name'] for col in response["ColumnInfo"]]
columns_type = [col["Type"]['ScalarType'] for col in response["ColumnInfo"]]

rows = [row["Data"] for row in response["Rows"]]
rows_list = [[next(iter(el.values())) for el in row] for row in rows]

df = pd.DataFrame(rows_list, columns=columns_name)
df.time = df.time.dt.tz_localize('UTC').dt.tz_convert('Australia/ACT')
```

