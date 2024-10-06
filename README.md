# AgenticDB

A core problem facing GenAI agents today is the proliferation of different frameworks—such as LangGraph, AWS Bedrock, Semantic Kernel, among others—and the lack of interoperability between them. Regardless of the framework and runtime you choose, you might need to use or interoperate with agents from different frameworks, APIs, or legacy enterprise applications.

Therefore, it becomes paramount to search for available agents for a certain task and determine how to use them to solve a problem. This database incorporates the idea of agent and application manifests to facilitate this process.

**AgenticDB** is a database designed to store and manage GenAI agent and agentic application manifests. It enables developers and users to easily add, search, invoke, and rate agents while supporting advanced use cases like Docker-based agent management and remote execution. With its ability to handle agentic applications, AgenticDB is highly adaptable for a wide variety of GenAI workflows.

With **AgenticDB**, you can:

- **Store** and manage agent manifests.
- **Search** for agents using similarity search.
- **Invoke** agents via local and remote execution models.
- **Rate** agents based on performance and interaction results.

---

## Table of Contents

- [AgenticDB](#agenticdb)
  - [Table of Contents](#table-of-contents)
  - [Run Server](#run-server)
  - [Delete All Collections](#delete-all-collections)
    - [cURL Command](#curl-command)
    - [Response](#response)
      - [Example Response:](#example-response)
    - [Explanation](#explanation)
  - [Add an Agent](#add-an-agent)
  - [Search for Agents (Similarity Search)](#search-for-agents-similarity-search)
  - [Add an Application](#add-an-application)
  - [Invoke an Agent with cURL](#invoke-an-agent-with-curl)
  - [Rate an Agent](#rate-an-agent)
  - [Retrieve Ratings](#retrieve-ratings)

---

## Run Server

To start the AgenticDB server locally, run the following command:

```bash
python server.py
```

The API will be available at `http://127.0.0.1:8000`.

Here's an updated version of the **Delete All Collections** section in the README, reflecting the actual JSON response format from the provided Python code.

---

## Delete All Collections

You can delete all agent, application, and rating collections from AgenticDB with a single `DELETE` request. This operation will attempt to remove the stored collections: `agents`, `applications`, and `ratings`. Each collection deletion is handled separately, and the results will reflect whether each collection was successfully deleted.

### cURL Command

```bash
curl -X DELETE "http://127.0.0.1:8000/collections"
```

### Response

The response will provide the status of each deletion attempt in the form of a JSON object. If a collection is successfully deleted, the value will be `0`. If there was an error, the value will contain the corresponding error message.

#### Example Response:

```json
{
    "agents": 0,
    "applications": 0,
    "ratings": "Failed to delete ratings collection: some_error_message"
}
```

### Explanation

- **agents**: `0` indicates the `agents` collection was successfully deleted.
- **applications**: `0` indicates the `applications` collection was successfully deleted.
- **ratings**: Contains an error message if the deletion failed (replace `"some_error_message"` with the actual error encountered).

## Add an Agent

You can add an agent to the database using the following `curl` command. This example sends a JSON request to add a new agent called `code-gen-chart-agent`.

```bash
curl -X POST "http://127.0.0.1:8000/agents" \
     -H "Content-Type: application/json" \
     -H "Accept: application/json" \
     -d '[
            {
                "metadata": {
                    "name": "code-gen-chart-agent",
                    "namespace": "agents",
                    "description": "Requests for a javascript code generator to plot a chart with supplied free-form data."
                },
                "spec": {
                    "type": "agent",
                    "lifecycle": "dev",
                    "owner": "admin@company.com",
                    "access_level": "Public",
                    "category": "Natural Language",
                    "url": "https://api.example.com/code-gen-chart-agent/agent",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The request message for the chart code generator agent."
                            },
                            "thread": {
                                "type": "string",
                                "description": "The id to separate parallel message threads."
                            }
                        },
                        "required": ["message", "thread"],
                        "additionalProperties": false
                    },
                    "output": {
                        "type": "string",
                        "description": "The result of the request, including any generated image location."
                    }
                }
            }
        ]'
```

This will add the agent manifest to AgenticDB, making it available for future searches and invocations.

---

## Search for Agents (Similarity Search)

To search for agents based on a natural language query, use the following `curl` command. This example searches for agents related to "Natural Language."

```bash
curl -G "http://127.0.0.1:8000/agents" \
     -H "Accept: application/json" \
     --data-urlencode "query=Which agents have a category of Natural Language?"
```

AgenticDB will perform a similarity search and return a list of matching agents based on the query.

---

## Add an Application

You can also add an agentic application to AgenticDB using a similar `curl` command. Here’s an example for adding a "Stock Price Charting Application" that tracks stock prices and generates charts.

```bash
curl -X POST "http://127.0.0.1:8000/applications" \
     -H "Content-Type: application/json" \
     -H "Accept: application/json" \
     -d '[
            {
                "metadata": {
                    "name": "Stock Price Charting Application",
                    "namespace": "production",
                    "description": "Provides access to daily open, high, low, close stock prices over time and the ability to generate charts for the requested data"
                },
                "spec": {
                    "type": "application",
                    "lifecycle": "dev",
                    "owner": "admin@company.com",
                    "access_level": "PUBLIC",
                    "category": "Finance",
                    "setup": {
                        "compose": {
                            "compose_url": "https://ipfs.filebase.io/ipfs/somehash",
                            "run_command": "gunzip docker-compose.yml.gz && docker compose -f ./docker-compose.yml up -d"
                        }
                    },
                    "url": "http://localhost:3000/agent",
                    "method": "POST",
                    "example": "http://localhost:3000/agent 'Content-Type':'application/json' {'input':'what was the Nvidia close price on August 22nd 2024', 'thread':'nvidia'}",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "input": {
                                "type": "string",
                                "description": "natural language request for stock price data and charting of the data as required"
                                },
                                "thread": {
                                    "type": "string",
                                    "description": "thread context id for the request"
                                }
                        },
                        "required": ["input"],
                        "additionalProperties": false
                    },
                    "output": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "the natural language response and the Final Answer to the request with a chart location if requested"
                            }
                        },
                        "description": "the answer to the request"
                    }
                }
            }
        ]'
```

---

## Invoke an Agent with cURL

To invoke an agent via cURL, you can send a request to the agent's specific endpoint. For example, to invoke the `joke-agent`, use the following command:

```bash
curl -X POST "http://127.0.0.1:8000/joke/invoke" \
     -H "Content-Type: application/json" \
     -d '{"input": {"topic": "cats"}}'
```

This will invoke the `joke-agent` with the topic "cats" and return a joke response.

---

## Rate an Agent

After interacting with an agent, you can submit a rating for the agent using this `curl` command. Replace `placeholder_agent_id` and `placeholder_some_id` with the actual agent and rating IDs.

```bash
curl -X POST "http://127.0.0.1:8000/ratings" \
     -H "Content-Type: application/json" \
     -d '{
           "ratings": {
               "agent_id": "placeholder_agent_id",
               "id": "placeholder_some_id",
               "data": {
                   "score": 4
               }
           }
         }'
```

---

## Retrieve Ratings

You can retrieve agent ratings using this `curl` command. Replace `<ratings_id>` with the actual ratings ID.

```bash
curl -X GET "http://127.0.0.1:8000/ratings?ratings_id=<ratings_id>"
```

AgenticDB will return the score and feedback associated with the provided ratings ID.

---

This enhanced README focuses on executing the operations stand-alone via `curl` commands, emphasizing how to interact with agents and applications directly through HTTP requests. It introduces AgenticDB as a powerful tool for managing GenAI agents and applications, enabling seamless search, invocation, and rating functionality.
