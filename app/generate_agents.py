import yaml
import uuid

base_yaml = """
metadata:
  id: {id}
  name: {name}
  namespace: {namespace}
  description: |
    {description}
spec:
  type: agent
  lifecycle: {lifecycle}
  owner: {owner}
  access_level: {access_level}
  category: {category}
  url: {url}
  input:
    type: {input_type}
    description: {input_description}
  output:
    type: {output_type}
    description: {output_description}
"""

domains = ["example.com", "company.com", "service.com", "platform.com", "business.com"]
categories = ["Finance", "Customer Support", "Weather", "Health", "E-commerce", "Education", "Technology", "Transport", "Media", "Sports"]
input_output_types = ["string", "integer", "boolean", "object", "array"]
descriptions = [
    "Retrieves financial price data for a variety of tickers and timeframes.",
    "Assists customers with their queries and issues in real-time.",
    "Provides accurate and timely weather forecasts for various regions.",
    "Automates stock trading based on market analysis and trends.",
    "Monitors health metrics and provides insights for better health management.",
    "Manages e-commerce transactions and customer data.",
    "Delivers educational content and manages student information.",
    "Tracks and optimizes transportation logistics.",
    "Streams media content and manages user subscriptions.",
    "Analyzes sports performance and provides real-time updates."
]

agents = []

# Generate initial 5 agents with predefined data
for i in range(5):
    agents.append({
        "id": str(uuid.uuid4()),
        "name": f"agent-{i + 1}",
        "namespace": "sandbox" if i % 2 == 0 else "production",
        "description": descriptions[i % len(descriptions)],
        "lifecycle": "experimental" if i % 2 == 0 else "stable",
        "owner": f"owner{i + 1}@{domains[i % len(domains)]}",
        "access_level": "PRIVATE" if i % 2 == 0 else "PUBLIC",
        "category": categories[i % len(categories)],
        "url": f"https://api.{domains[i % len(domains)]}/agent-{i + 1}",
        "input_type": input_output_types[i % len(input_output_types)],
        "input_description": f"Input description for agent-{i + 1}",
        "output_type": input_output_types[(i + 1) % len(input_output_types)],
        "output_description": f"Output description for agent-{i + 1}"
    })

# Generate additional agents to make a total of 50 agents
for i in range(45):
    domain = domains[i % len(domains)]
    category = categories[i % len(categories)]
    agents.append({
        "id": str(uuid.uuid4()),
        "name": f"agent-{i + 6}",
        "namespace": "sandbox" if i % 2 == 0 else "production",
        "description": f"Description for agent-{i + 6}",
        "lifecycle": "experimental" if i % 2 == 0 else "stable",
        "owner": f"owner{i + 6}@{domain}",
        "access_level": "PRIVATE" if i % 2 == 0 else "PUBLIC",
        "category": category,
        "url": f"https://api.{domain}/agent-{i + 6}",
        "input_type": input_output_types[i % len(input_output_types)],
        "input_description": f"Input description for agent-{i + 6}",
        "output_type": input_output_types[(i + 1) % len(input_output_types)],
        "output_description": f"Output description for agent-{i + 6}"
    })

yaml_content = ""
for agent in agents:
    yaml_content += base_yaml.format(
        id=agent["id"],
        name=agent["name"],
        namespace=agent["namespace"],
        description=agent["description"],
        lifecycle=agent["lifecycle"],
        owner=agent["owner"],
        access_level=agent["access_level"],
        category=agent["category"],
        url=agent["url"],
        input_type=agent["input_type"],
        input_description=agent["input_description"],
        output_type=agent["output_type"],
        output_description=agent["output_description"]
    ) + "\n"

with open("agents.yaml", "w") as file:
    file.write(yaml_content)

print("Generated agents.yaml with 50 agent specifications.")
