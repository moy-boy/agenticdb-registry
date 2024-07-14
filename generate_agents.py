import yaml

base_yaml = """
metadata:
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
"""

domains = ["example.com", "company.com", "service.com", "platform.com", "business.com"]
categories = ["Finance", "Customer Support", "Weather", "Health", "E-commerce", "Education", "Technology", "Transport", "Media", "Sports"]

agents = [
    {
        "name": "financial-data-oracle",
        "namespace": "sandbox",
        "description": "Retrieves financial price data for a variety of tickers and timeframes.",
        "lifecycle": "experimental",
        "owner": "buddy@example.com",
        "access_level": "PRIVATE",
        "category": "Finance"
    },
    {
        "name": "customer-support-chatbot",
        "namespace": "production",
        "description": "Assists customers with their queries and issues in real-time.",
        "lifecycle": "stable",
        "owner": "support@company.com",
        "access_level": "PUBLIC",
        "category": "Customer Support"
    },
    {
        "name": "weather-forecasting-service",
        "namespace": "sandbox",
        "description": "Provides accurate and timely weather forecasts for various regions.",
        "lifecycle": "experimental",
        "owner": "weather@service.com",
        "access_level": "PRIVATE",
        "category": "Weather"
    },
    {
        "name": "stock-trading-bot",
        "namespace": "production",
        "description": "Automates stock trading based on market analysis and trends.",
        "lifecycle": "stable",
        "owner": "trader@platform.com",
        "access_level": "PRIVATE",
        "category": "Finance"
    },
    {
        "name": "health-monitoring-system",
        "namespace": "sandbox",
        "description": "Monitors health metrics and provides insights for better health management.",
        "lifecycle": "experimental",
        "owner": "health@business.com",
        "access_level": "PRIVATE",
        "category": "Health"
    },
]

# Generate additional agents to make a total of 50 agents
for i in range(45):
    domain = domains[i % len(domains)]
    category = categories[i % len(categories)]
    agents.append({
        "name": f"agent-{i + 6}",
        "namespace": "sandbox" if i % 2 == 0 else "production",
        "description": f"Description for agent-{i + 6}",
        "lifecycle": "experimental" if i % 2 == 0 else "stable",
        "owner": f"owner{i + 6}@{domain}",
        "access_level": "PRIVATE" if i % 2 == 0 else "PUBLIC",
        "category": category
    })

yaml_content = ""
for agent in agents:
    yaml_content += base_yaml.format(
        name=agent["name"],
        namespace=agent["namespace"],
        description=agent["description"],
        lifecycle=agent["lifecycle"],
        owner=agent["owner"],
        access_level=agent["access_level"],
        category=agent["category"]
    ) + "\n"

with open("agents.yaml", "w") as file:
    file.write(yaml_content)

print("Generated agents.yaml with 50 agent specifications.")
