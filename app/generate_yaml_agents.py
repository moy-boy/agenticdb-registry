import random

base_yaml = """
---
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
  url: {url}
  parameters:
    type: object
    properties:
{properties}
    required:
{required}
    additionalProperties: false
  output:
    type: {output_type}
    description: {output_description}
"""

domains = ["example.com", "company.com", "service.com", "platform.com", "business.com"]
categories = ["Finance", "Customer Support", "Weather", "Health", "E-commerce", "Education", "Technology", "Transport", "Media", "Sports", "Travel", "Clothing", "Logistics"]
property_names = [
    "symbol", "date", "currency", "amount", "location", "product_id", "transaction_id", "user_id", "timestamp",
    "language", "destination", "departure_time", "arrival_time", "seat_number", "flight_number", "hotel_name",
    "room_type", "check_in_date", "check_out_date", "clothing_size", "color", "material", "order_id", "delivery_date",
    "tracking_number", "support_ticket_id", "customer_name", "issue_type", "resolution_status"
]
property_types = ["string", "integer", "boolean", "float"]
property_descriptions = [
    "Ticker symbol for financial data", "A specific date in the format yyyy-mm-dd", "The currency of the transaction",
    "The amount for the transaction", "The location of the event", "The product ID for the item",
    "The transaction ID for the order", "The user ID for the customer", "The timestamp of the event",
    "The language code for the content", "The destination for travel", "Departure time for the journey",
    "Arrival time at the destination", "The seat number for the passenger", "Flight number for the airline",
    "The hotel name for the booking", "Type of room in the hotel", "Check-in date at the hotel",
    "Check-out date from the hotel", "Size of the clothing item", "Color of the item", "Material of the product",
    "The order ID for the purchase", "Expected delivery date", "Tracking number for the shipment",
    "Support ticket ID for the issue", "Name of the customer", "Type of issue reported",
    "Status of the issue resolution"
]
output_types = ["string", "integer", "boolean", "float"]
output_descriptions = [
    "Output value for the requested data", "Result of the operation", "Boolean flag indicating success or failure",
    "Calculated amount based on the input data", "Status of the operation", "Summary of the processed information",
    "ID of the created resource", "Confirmation message for the user"
]

agents = []

# Generate 50 agents with varied data
for i in range(50):
    properties = []
    required_fields = []
    num_properties = random.randint(2, 5)  # Number of properties to include
    used_property_names = set()

    for _ in range(num_properties):
        while True:
            property_name = random.choice(property_names)
            if property_name not in used_property_names:
                used_property_names.add(property_name)
                break
        property_type = random.choice(property_types)
        property_description = random.choice(property_descriptions)
        properties.append(f"      {property_name}:\n        type: {property_type}\n        description: \"{property_description}\"")
        if random.choice([True, False]):
            required_fields.append(f"      - {property_name}")

    properties_yaml = "\n".join(properties)
    required_yaml = "\n".join(required_fields) if required_fields else "      - "

    agents.append({
        "name": f"agent-{i + 1}",
        "namespace": "sandbox" if i % 2 == 0 else "production",
        "description": f"Description for agent-{i + 1}",
        "lifecycle": "experimental" if i % 2 == 0 else "stable",
        "owner": f"owner{i + 1}@{domains[i % len(domains)]}",
        "access_level": "PRIVATE" if i % 2 == 0 else "PUBLIC",
        "category": categories[i % len(categories)],
        "url": f"https://api.{domains[i % len(domains)]}/agent-{i + 1}",
        "properties": properties_yaml,
        "required": required_yaml,
        "output_type": random.choice(output_types),
        "output_description": random.choice(output_descriptions)
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
        category=agent["category"],
        url=agent["url"],
        properties=agent["properties"],
        required=agent["required"],
        output_type=agent["output_type"],
        output_description=agent["output_description"]
    ) + "\n"

with open("agents.yaml", "w") as file:
    file.write(yaml_content)

print("Generated agents.yaml with 50 varied agent specifications.")
