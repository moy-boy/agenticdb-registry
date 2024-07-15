# AgenticDB

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

```shell

curl -G "http://127.0.0.1:8000/agents" \
     --data-urlencode "query=Which agents have a category of Natural Language?"


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