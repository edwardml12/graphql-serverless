import os
import json
from ariadne import QueryType, MutationType, make_executable_schema, load_schema_from_path, graphql_sync
from ariadne.constants import PLAYGROUND_HTML
from entity.character import Character
from infra.character import DynamoRepository

type_defs = load_schema_from_path("schema.graphql")

query = QueryType()
mutation = MutationType()

repository = DynamoRepository()

@query.field("getCharacter")
def resolve_get_character(_, info, name):
    
    characterDB = repository._get_by_name(name)
    if not characterDB:
        raise ValueError(f"Character with name '{name}' does not exist.")
    character = Character(**characterDB)

    return {
        "name": character.name,
        "health": character.health,
        "is_alive": character.is_alive,
        "killed_by": character.killed_by,
    }

@mutation.field("createCharacter")
def resolve_create_character(_, info, input):
    killers = []
    for killer_name in input.get("killed_by"):
        characterDB = repository._get_by_name(killer_name)
        if not characterDB:
            raise ValueError(f"Character with name '{killer_name}' does not exist.")
        killers.append(Character(**characterDB))
    character = Character(input["name"], input["health"], killed_by=killers)
    # repository._save(character.name, character.health, character.killed_by)
    return character

schema = make_executable_schema(type_defs, [query, mutation])

def handler(event, context):
    """
    Lambda entry point. Handles both GraphQL queries (POST) and
    Apollo Playground (GET).
    """
    # Support GraphQL Playground at GET /
    if event.get("httpMethod", "") == "GET":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": PLAYGROUND_HTML,
        }

    body = json.loads(event.get("body") or "{}")
    success, result = graphql_sync(
        schema,
        data=body,
        context_value= {"event": event, "context": context},
        debug= os.environ.get("DEBUG", "false").lower() == "true",
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result),
    }


