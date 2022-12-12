# Lambda Python Code Examples
You can find all the examples source code files undes 'src/code'.

All examples are based on the BrewAI IAQ project.

***List of examples:***

| Filename | Description |
| ------------ | ------------- |
| table_get.py | Get endpoint for API Gateway that query items from dynamodb. |
| table_put.py | Put endpoint for API Gateway that insert items in dynamodb. |
| manage_conn.py | Connections manager for websocket api. |
| msg_conn.py | Message sender for websocket api. |
| timestream_get.py | Get endpoint for API Gateway that query items from timestream. |
| timestream_put.py | Put endpoint for API Gateway that upsert items on timestream. |
| brewai_fetch.py | Scheduled lambdas that retreive latest data from api and insert in our own system. |
| make_prediction.py | Lambdas that generate predictions for a specific timestamp using databricks inference api. |

## Lambda Python specificities
The python runtime environement is a litle bit special, here is some particularities.

## 1. Logging
The default logger outputs logs in the Cloudwhatch Logs. Therefor, you can log this way.

```python
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def handler(event, context):
    LOGGER.info("Some info")
    LOGGER.warning("Some warning")
    LOGGER.error("Some error")
```

## 2. Traceback and errors
Debuging a lambda function can be tricky. Logging the error won't print the traceback. Use the traceback package.
```python
import logging
import traceback

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def handler(event, context):
    try:
        your_lambda_logic()
        ...
    except Exception as e:
        LOGGER.error(f"Something went wrong {e}")
        traceback.print_exc()
        return {"statusCode": 500}
```

## 3. No requests package
The requests package is not available in AWS runtime. We can use urllib3 instead.

```python
import logging
import traceback
import urllib3
import json

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def handler(event, context):
    try:
        http = urllib3.PoolManager()
        get_response = http.request(
            "GET",
            url="...",
            headers={},
        )
        my_data = json.loads(get_response.data)

        put_response = http.request(
            "PUT",
            url="...",
            headers={},
            body=json.dumps(my_data),
        )

        if put_response.status != 200:
            LOGGER.warning("Put request failed")
        ...
    except Exception as e:
        LOGGER.error(f"Something went wrong {e}")
        traceback.print_exc()
```
    