#!/bin/bash

# Default URL if not provided
url="http://127.0.0.1:8000/agents"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --url) url="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# ADD AN AGENT
curl -X POST "$url" \
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
