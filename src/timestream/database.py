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

        TimestreamwriteTable(
            self,
            "table",
            database_name=db.database_name,
            table_name=table_name,
            retention_properties=dict(
                magnetic_store_retention_period_in_days=1,
                memory_store_retention_period_in_hours=12,
            ),
            tags=tags,
        )
