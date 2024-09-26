#!/bin/bash

# ADD AN APPLICATION

# Default URL if not provided
url="http://127.0.0.1:8000/applications"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --url) url="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

curl -X POST "$url" \
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
