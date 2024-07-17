# AgenticDB

Wouldn't be cool if you could store and search for GenAI agents in a database? And when you found one you liked, you could invoke it remotely?

The icing on the cake is that you can also rate your experience with the agent and provide feedback to the agent owner.

This is an implementation of a VectorDB that stores GenAI Agent manifests. It supports adding and searching for agents.
When searching for an agent (see example), similarity search is used, a 
maximum of 4 agents are returned

It comes with a built-in example agent that tells jokes to show remote execution of agent code chains 
based on the URL in the manifest. In order to invoke the agent you need a `.env` file with the following content:

```shell
OPENAI_API_KEY=<openai key>
OPENAI_MODEL_NAME=gpt-4o
````

## Server

Run Server

```shell
python server.py
```


## Add Agent

```shell

curl -X POST "http://127.0.0.1:8000/agents" \
     -H "Content-Type: application/x-yaml" \
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
  input:
    type: string
    description: Input description for financial-data-oracle
  output:
    type: string
    description: Output description for financial-data-oracle
EOF

```

Response:

```json
{
    "original_content": "metadata:\n  description: 'Retrieves financial price data for a variety of tickers and timeframes.\n\n    '\n  id: bd833e57-97e6-4586-8c40-fd1ebf92e7af\n  name: financial-data-oracle\n  namespace: sandbox\n  ratings: c5fa8063-0718-4d6b-8296-f99371344f40\nspec:\n  access_level: PRIVATE\n  category: Natural Language\n  input:\n    description: Input description for financial-data-oracle\n    type: string\n  lifecycle: experimental\n  output:\n    description: Output description for financial-data-oracle\n    type: string\n  owner: buddy@example.com\n  type: agent\n  url: https://api.example.com/financial-data-oracle\n",
    "parsed_content": {
        "metadata": {
            "name": "financial-data-oracle",
            "namespace": "sandbox",
            "description": "Retrieves financial price data for a variety of tickers and timeframes.\n",
            "id": "bd833e57-97e6-4586-8c40-fd1ebf92e7af",
            "ratings": "c5fa8063-0718-4d6b-8296-f99371344f40"
        },
        "spec": {
            "type": "agent",
            "lifecycle": "experimental",
            "owner": "buddy@example.com",
            "access_level": "PRIVATE",
            "category": "Natural Language",
            "url": "https://api.example.com/financial-data-oracle",
            "input": {
                "type": "string",
                "description": "Input description for financial-data-oracle"
            },
            "output": {
                "type": "string",
                "description": "Output description for financial-data-oracle"
            }
        }
    },
    "agent_id": "bd833e57-97e6-4586-8c40-fd1ebf92e7af",
    "ratings_id": "c5fa8063-0718-4d6b-8296-f99371344f40",
    "ratings_manifest": {
        "id": "c5fa8063-0718-4d6b-8296-f99371344f40",
        "agent_id": "bd833e57-97e6-4586-8c40-fd1ebf92e7af",
        "data": {
            "score": 0,
            "samples": 0
        }
    }
}
```
## Search for Agents (similarity search)

```shell

curl -G "http://127.0.0.1:8000/agents" \
     --data-urlencode "query=Which agents have a category of Natural Language?"
```

Response

```json
{
  "agents": "---\nmetadata:\n  name: financial-data-oracle\n  namespace: sandbox\n  description: 'Retrieves financial price data for a variety of tickers and timeframes.\n\n    '\n  id: 09e3e7b1-37b2-4eb4-b372-d94cdff05a75\n  ratings: 1bcba589-3366-4fea-be78-5b5ad0daf93f\nspec:\n  type: agent\n  lifecycle: experimental\n  owner: buddy@example.com\n  access_level: PRIVATE\n  category: Natural Language\n  url: https://api.example.com/financial-data-oracle\n  input:\n    type: string\n    description: Input description for financial-data-oracle\n  output:\n    type: string\n    description: Output description for financial-data-oracle\nratings:\n  id: 1bcba589-3366-4fea-be78-5b5ad0daf93f\n  agent_id: 09e3e7b1-37b2-4eb4-b372-d94cdff05a75\n  data:\n    score: 0\n    samples: 0"
}
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