import json
from constructs import Construct
from cdktf import TerraformOutput
from cdktf_cdktf_provider_aws.data_aws_iam_policy_document import (
    DataAwsIamPolicyDocument,
)
from cdktf_cdktf_provider_aws.iam_policy import IamPolicy
from cdktf_cdktf_provider_aws.iam_role import IamRole
from cdktf_cdktf_provider_aws.timestreamwrite_database import (
    TimestreamwriteDatabase,
)
from cdktf_cdktf_provider_aws.timestreamwrite_table import (
    TimestreamwriteTable,
)


class Timestream(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        table_name: str,
        tags: dict,
    ):
        super().__init__(scope, id)

        db = TimestreamwriteDatabase(
            self,
            "db",
            database_name=f'ProjectTable-{tags["project"]}-{tags["env"]}',
            tags=tags,
        )

        table = TimestreamwriteTable(
            self,
            "table",
            database_name=db.database_name,
            table_name=table_name,
            retention_properties=dict(
                magnetic_store_retention_period_in_days=30,
                memory_store_retention_period_in_hours=24,
            ),
            tags=tags,
        )

        table_crud = IamPolicy(
            self,
            "table-crud",
            name=f"{table.database_name}-{table.table_name}-CRUD",
            policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": [
                                "timestream:DescribeEndpoints",
                                "timestream:DescribeTable",
                                "timestream:DescribeDatabase",
                                "timestream:ListTables",
                                "timestream:ListDatabases",
                            ],
                            "Resource": ["*"],
                            "Effect": "Allow",
                        },
                        {
                            "Action": [
                                "timestream:WriteRecords",
                                "timestream:WriteRecords",
                                "timestream:ListMeasures",
                                "timestream:Select",
                            ],
                            "Resource": [table.arn],
                            "Effect": "Allow",
                        },
                    ],
                }
            ),
            tags=tags,
        )

        self.crud_arn = table_crud.arn
        self.db_name = db.database_name
        self.table_name = table.table_name
