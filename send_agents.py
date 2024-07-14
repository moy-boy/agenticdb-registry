import requests
import yaml

with open("agents.yaml", "r") as file:
    agents_yaml = file.read()

# Split the file content into individual YAML documents
agents = list(yaml.safe_load_all(agents_yaml))

url = "http://127.0.0.1:8000/agent"

headers = {'Content-Type': 'application/x-yaml'}

for agent in agents:
    agent_yaml_str = yaml.dump(agent)
    response = requests.post(url, data=agent_yaml_str, headers=headers)
    if response.status_code == 200:
        print(f"Successfully sent agent: {agent['metadata']['name']}")
    else:
        print(f"Failed to send agent: {agent['metadata']['name']}, Status Code: {response.status_code}, Response: {response.text}")
