from abc import ABC, abstractmethod
from typing import List, Dict

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from dotenv import load_dotenv
import os

#  Carregando variáveis de ambiente
load_dotenv()
## Credenciais da AWS
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS = os.getenv("AWS_SECRET_ACCESS")

dynamodb = boto3.resource(
    "dynamodb",
    region_name="sa-east-1",  
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_ACCESS,
)
table = dynamodb.Table("characters")

class DynamoRepository():
    def _save(self, name: str, health: int, killed_by: List) -> None:
        try:
            table.put_item(
                Item={
                    "name": name,
                    "health": health,
                    "killed_by": killed_by,
                },
                ConditionExpression="attribute_not_exists(name)"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                print(f"Item with name '{name}' already exists.")
            else:
                print("Error saving item to DynamoDB")
                print(e.response["Error"]["Message"])
        pass

    def _get_by_name(self, name: str, isKiller: bool = False) -> Dict:
        """
        Get a character by name from the database.
        """
        try:
            response = table.get_item(Key={"name": name})
        except ClientError as e:
            print("Error getting item from DynamoDB")
            print(e.response["Error"]["Message"])
            return None
        
        character = response.get("Item")
        if character is None:
            return None
        
        if not isKiller and character.get("killed_by") is not None :
            character["killed_by"] = self._get_killers(character.get("killed_by"))
        return character

    def _get_killers(self, killers: List[str]) -> List[Dict]:
        """
        Get the killers from the database.
        """
        killers = []
        for killer_name in killers:
            killer = self._get_by_name(killer_name, True)
            if killer is not None:
                killers.append(killer)
        return killers