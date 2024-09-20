# AgenticDB

- [AgenticDB](#agenticdb)
  - [Run Server](#run-server)
  - [Add Agent](#add-agent)
  - [Search for Agents (similarity search)](#search-for-agents-similarity-search)
  - [Add a Docker Agent](#add-a-docker-agent)
  - [Invoke Example Joke Agent with cURL](#invoke-example-joke-agent-with-curl)
  - [Invoke Example Joke Agent with Remote Execution](#invoke-example-joke-agent-with-remote-execution)
  - [Rate an Agent ★★★★☆](#rate-an-agent-)
  - [Retrieve Ratings](#retrieve-ratings)


![Agentic Dashboard](docs/images/landing.png "Agentic Dashboard Screenshot")

Wouldn't be cool if you could store and search for GenAI agents in a database? And when you found one you liked, you could invoke it remotely?

The icing on the cake is that you can also rate your experience with the agent and provide feedback to the agent owner.

This is an implementation of a VectorDB that stores GenAI Agent manifests. It supports adding and searching for agents.
When searching for an agent (see example), similarity search is used, a maximum of 10 agents are returned

It comes with a built-in example agent that tells jokes to show remote execution of agent code chains based on the URL in the manifest. In order to invoke the agent you need a `.env` file with the following content:

```shell
OPENAI_API_KEY=<openai key>
OPENAI_MODEL_NAME=gpt-4o
````

**If you do not plan to remote invoke an agent, there is no dependency on OpenAI.**

## Run Server

Run Server

```shell
python server.py
```

## Add Agent

The API supports both JSON and YAMl agent monifests.  The example below uses YAML but a similar example can use JSON. You can find many examples under the `tests` folder.

Notice that both `Content-Type` and `Accept-Encoding` are mandatory so Server knows the preferred format, YAML or JSON.

```shell

curl -X POST "http://127.0.0.1:8000/agents" \
     -H "Content-Type: application/x-yaml" \
     -H "Accept-Encoding: x-yaml" \
     --data-binary @- <<EOF
metadata:
  name: financial-data-oracle
  namespace: sandbox
  description: |
    Retrieves financial price data for a variety of tickers and timeframes.
spec:
  type: agent
  lifecycle: experimental
  owner: buddy@example.com
  access_level: PRIVATE
  category: Natural Language
  url: https://api.example.com/financial-data-oracle
  parameters:
    type: object
    properties:
      symbol:
        type: string
        description: ticker symbol
      date:
        type: string
        description: A specific date in the format yyyy-mm-dd
      currency:
        type: string
        enum:
          - USD
          - JPY
        description: "the currency of the desired output value"
    required:
      - symbol
    additionalProperties: false
  output:
    type: float
    description: Output description for financial-data-oracle
EOF
```

Response:

```yaml

```

## Search for Agents (similarity search)

```shell

curl -G "http://127.0.0.1:8000/agents" \
     -H "Accept-Encoding: application/x-yaml" 
     --data-urlencode "query=Which agents have a category of Natural Language?"
```

Response

```yaml
---
metadata:
  name: financial-data-oracle
  namespace: sandbox
  description: 'Retrieves financial price data for a variety of tickers and timeframes.

    '
  id: 413c718e-e686-4fdf-bb3e-91c44fc94c7c
  ratings_id: 8b9b8114-f69c-4cf0-a723-8239c33cb5b5
spec:
  type: agent
  lifecycle: experimental
  owner: buddy@example.com
  access_level: PRIVATE
  category: Natural Language
  url: https://api.example.com/financial-data-oracle
  parameters:
    type: object
    properties:
      symbol:
        type: string
        description: ticker symbol
      date:
        type: string
        description: A specific date in the format yyyy-mm-dd
      currency:
        type: string
        enum:
        - USD
        - JPY
        description: the currency of the desired output value
    required:
    - symbol
    additionalProperties: false
  output:
    type: float
    description: Output description for financial-data-oracle
```

## Add a Docker Agent

```
curl -X POST http://localhost:8000/agents \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '[
    {
        "metadata": {
            "name": "Inventory Agent",
            "namespace": "production",
            "description": "Keeps track of item ids"
        },
        "spec": {
            "type": "agent",
            "lifecycle": "stable",
            "owner": "owner50@business.com",
            "access_level": "PUBLIC",
            "category": "Travel",
            "setup": {
                "docker": {
                    "registry_url": "https://index.docker.io/v1/",
                    "image_name": "rapenno/fastapi_agent",
                    "image_tag": "latest",
                    "run_command": "docker run -d -p 8001:8001 rapenno/fastapi_agent"
                }
            },
            "url": "http://localhost:8001/items/{itemid}",
            "method": "GET",
            "example": "http://localhost:8001/items/5?q=somequery",
            "parameters": {
                "type": "object",
                "properties": {
                    "itemid": {
                        "type": "integer",
                        "description": "item number"
                    },
                    "query": {
                        "type": "string",
                        "description": "a query string"
                    }
                },
                "required": [
                    "itemid",
                    "query"
                ],
                "additionalProperties": false
            },
            "output": {
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "integer",
                        "description": "the item id"
                    },
                    "q": {
                        "type": "string",
                        "description": "query string"
                    }
                },
                "description": "Boolean flag indicating success or failure"
            }
        }
    }
]'
```

## Invoke Example Joke Agent with cURL

```shell
curl -X POST "http://127.0.0.1:8000/joke/invoke" \
     -H "Content-Type: application/json" \
     -d '{"input": {"topic": "cats"}}'
```

## Invoke Example Joke Agent with Remote Execution

```python
from langserve import RemoteRunnable

joke_chain = RemoteRunnable("http://localhost:8000/joke/")

response = joke_chain.invoke({"topic": "parrots"})
print(response.content)
```

## Rate an Agent ★★★★☆

```shell
curl -X POST "http://127.0.0.1:8000/ratings" \
     -H "Content-Type: application/x-yaml" \
     --data-binary @- <<EOF
ratings:
  agent_id: placeholder_agent_id  # Replace with actual agent_id
  id: placeholder_some_id         # Replace with actual ratings_id
  data:
    score: <score>                # Example with 3 stars: ★★★☆☆
EOF

```

Response:

```json
{
    "ratings": {

        "id":"1bcba589-3366-4fea-be78-5b5ad0daf93f",
        "agent_id":"09e3e7b1-37b2-4eb4-b372-d94cdff05a75",
        "data": {
            "score": 3.0, "samples":1
        }
    }
}
```

## Retrieve Ratings

```shell
curl -X GET "http://127.0.0.1:8000/ratings?ratings_id=<ratings_id>"
```

Response

```json
{

    "agent_id":"09e3e7b1-37b2-4eb4-b372-d94cdff05a75",
    "data": {
        "samples": 1, "score":3.0
    }

    ,
    "id":"1bcba589-3366-4fea-be78-5b5ad0daf93f"
}
```