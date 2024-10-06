# AgenticDB Registry

AgenticDB Registry is a lightweight registry and API service for GenAI agents and agentic applications. It stores structured manifests for agents, applications, and ratings so teams can discover available capabilities, search for suitable agents, invoke them, and track feedback from interactions.

The project addresses a common problem in agent-based systems: agents are often scattered across different frameworks, APIs, local services, and deployment models. AgenticDB Registry provides a central place to describe those agents with metadata, input schemas, output schemas, lifecycle information, access level, category, ownership, and runtime details.

AgenticDB Registry exposes a FastAPI server for managing manifests and includes examples for adding agents, adding applications, searching agents by natural language query, invoking agents, resetting collections, and storing ratings. It also includes Docker-based examples for packaging remote runnable agents.

With **AgenticDB Registry**, you can:

- **Store** and manage agent manifests.
- **Search** for agents using similarity search.
- **Invoke** agents via local and remote execution models.
- **Rate** agents based on performance and interaction results.

---

## Table of Contents

- [AgenticDB Registry](#agenticdb-registry)
  - [Table of Contents](#table-of-contents)
  - [Run Server](#run-server)
  - [Add an Agent](#add-an-agent)
  - [Search for Agents (Similarity Search)](#search-for-agents-similarity-search)
  - [Add an Application](#add-an-application)
  - [Delete All Collections](#delete-all-collections)
    - [cURL Command](#curl-command)
    - [Response](#response)
      - [Example Response](#example-response)
    - [Explanation](#explanation)
  - [Rate an Agent](#rate-an-agent)
  - [Retrieve Ratings](#retrieve-ratings)

---

## Run Server

To start the AgenticDB Registry server locally, run the following command:

```bash
python server.py
```

The API will be available at `http://127.0.0.1:8000`.

---

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
                    "category": "Travel Agent",
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
     --data-urlencode "query=Which agents can book travel?"
```

AgenticDB Registry will perform a similarity search and return a list of matching agents based on the query.

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

## Delete All Collections

You can delete all agent, application, and rating collections from AgenticDB with a single `DELETE` request. This operation will attempt to remove the stored collections: `agents`, `applications`, and `ratings`. Each collection deletion is handled separately, and the results will reflect whether each collection was successfully deleted.

### cURL Command

```bash
curl -X DELETE "http://127.0.0.1:8000/collections"
```

### Response

The response will provide the status of each deletion attempt in the form of a JSON object. If a collection is successfully deleted, the value will be `0`. If there was an error, the value will contain the corresponding error message.

#### Example Response

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

AgenticDB Registry will return the score and feedback associated with the provided ratings ID.
