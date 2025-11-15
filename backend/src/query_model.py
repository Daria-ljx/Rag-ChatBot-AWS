from dataclasses import dataclass, asdict, field
import boto3
import uuid
from typing import List, Optional
import time
from botocore.exceptions import ClientError


TABLE_NAME = "rag"


# DynamoDB initialization
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


@dataclass
class QueryModel:
    query_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    create_time: int = field(default_factory=lambda: int(time.time()))
    query_text: str = ""
    answer_text: Optional[str] = None
    sources: Optional[List[str]] = field(default_factory=list)
    is_complete: bool = False


    # Storing the current object into DynamoDB
    def put_item(self):
        item = asdict(self)
        try:
            table.put_item(Item=item)
            print(f"✅ Saved item to DynamoDB: {self.query_id}")
        except ClientError as e:
            print("ClientError", e.response["Error"]["Message"])
            raise e

    # Get a query record from DynamoDB
    @classmethod
    def get_item(cls, query_id: str):
        try:
            response = table.get_item(Key={"query_id": query_id})
            item = response.get("Item")
        except ClientError as e:
            print("ClientError", e.response["Error"]["Message"])
            return None

        # ✅ Prevents item being None from causing **item to report an error.
        if not item:
            return None

        return cls(**item)
