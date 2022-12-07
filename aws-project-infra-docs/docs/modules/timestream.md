# Timestream database

Use this module to create a timestream database and table for the project.

## timestream.Timestream
Class for the Timestream Database and Table.

**Terraform resources:**

1. TimestreamwriteDatabase: The database.
2. TimestreamwriteTable: The table. Retention periods are set to 1 day of in-memory and 30 days of magnetic store.
3. IamPolicy: Policy that grant permission for CRUD opperation on table.

***Arguments***

| Name | Type | Description |
| ------------ | ------------- | ------------ |
| table_name | str | Name of the timestream table |
| tags | dict  | Tags for all resource, must include a 'project' and 'env' key |

***Attributes***

| Name | Type | Description |
| ------------ | ------------- | ------------ |
| crud_arn | str | ARN of the CRUD Policy |
| db_name | str | Name of the project database |
| table_name | str | Name of the project table |

## Example

Create a timestream database and table:
```python
from src.timestream import Timestream

tags = {
    "project": "My Project",
    "env": "dev"
}

table = Timestream(self, "timestram-id", "my_table", tags=tags)
```