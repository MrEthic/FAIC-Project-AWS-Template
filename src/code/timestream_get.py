import logging
import boto3
import traceback
import json
import os


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

REGION = os.environ.get("REGION", "ap-southeast-2")
session = boto3.Session(region_name=REGION)
timestream_client = session.client("timestream-query")

DATABASE_NAME = os.environ["DATABASE_NAME"]
TABLE_NAME = os.environ["TABLE_NAME"]
ATTRIBUTES = ["time_filter", "devIds", "measures"]


def build_query_one_measure(time_filter: str, measure: str, device_ids: list):
    device_filter = (
        f"""AND deviceId in {"('" + "', '".join(device_ids) + "')"}"""
        if len(device_ids) > 0
        else ""
    )
    QUERY = f"""
    SELECT 
        time,
        deviceId,
        measure_value::double AS {measure}
    FROM "{DATABASE_NAME}"."{TABLE_NAME}"
        WHERE
        {time_filter}
        AND measure_name='{measure}'
        {device_filter}
    ORDER BY time DESC
    """
    QUERY = " ".join([s.strip() for s in QUERY.split("\n")])
    return QUERY


def build_query(time_filter: str, measures: list, device_ids: list):
    device_filter = (
        f"""AND deviceId in {"('" + "', '".join(device_ids) + "')"}"""
        if len(device_ids) > 0
        else ""
    )
    QUERY = f"""
    SELECT 
        time,
        {
            "".join([f"MAX(if(measure_name = '{m}', measure_value::double)) AS {m}," for m in measures])
        }
        deviceId
    FROM "{DATABASE_NAME}"."{TABLE_NAME}"
        WHERE
        {time_filter}
        {device_filter}
    GROUP BY time, deviceId
    ORDER BY time DESC
    """
    QUERY = " ".join([s.strip() for s in QUERY.split("\n")])
    return QUERY


def handler(event, context):

    try:
        LOGGER.info(f"Received event: {event}")
        payload = json.loads(event["body"])

        if not all(key in payload.keys() for key in ATTRIBUTES):
            LOGGER.info(f"Missing parameters in requests.")
            return {
                "statusCode": 400,
                "body": '{"status":"Missing parameters."}',
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            }

        time_filter = payload["time_filter"]
        device_ids = payload["devIds"]
        measures = payload["measures"]

        if (
            type(time_filter) != str
            or type(device_ids) != list
            or type(measures) != list
        ):
            LOGGER.info(f"Invalid parameter types.")
            return {
                "statusCode": 400,
                "body": '{"status":"Invalid parameter types."}',
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            }

        if len(measures) == 1:
            QUERY = build_query_one_measure(time_filter, measures[0], device_ids)
        else:
            QUERY = build_query(time_filter, measures, device_ids)

        kwargs = {}
        if "nextToken" in payload:
            LOGGER.info("Found initial NextToken in query...")
            kwargs = {"NextToken": payload["nextToken"]}

        LOGGER.info(f"Executing SQL: {QUERY}")
        response = timestream_client.query(QueryString=QUERY, **kwargs)

        columns_name = [col["Name"] for col in response["ColumnInfo"]]
        columns_type = [col["Type"]["ScalarType"] for col in response["ColumnInfo"]]

        rows = [row["Data"] for row in response["Rows"]]
        n_iter = 0
        while "NextToken" in response and n_iter < 5:
            response = timestream_client.query(
                QueryString=QUERY, NextToken=response["NextToken"]
            )
            rows += [row["Data"] for row in response["Rows"]]
            n_iter += 1
            LOGGER.info(f"NextToken {n_iter} Consumed")

        rows_list = [[next(iter(el.values())) for el in row] for row in rows]

        LOGGER.info(f"Success {QUERY}")

        return {
            "statusCode": 201,
            "body": json.dumps(
                {
                    "Rows": rows_list,
                    "ColumnName": columns_name,
                    "ColumnType": columns_type,
                    "LastQueryId": response["QueryId"],
                    "NextTokenConsumed": n_iter,
                    "NextToken": response.get("NextToken", None),
                }
            ),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }
    except timestream_client.exceptions.ValidationException as err:
        LOGGER.error(f"ValidationException: {err}")
        return {
            "statusCode": 400,
            "body": '{"status":"Double check time filter syntax."}',
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }
    except Exception as e:
        LOGGER.error(f"Error inserting item: {e}")
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": '{"status":"Server error"}',
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }
