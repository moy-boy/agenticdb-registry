from copy import deepcopy
import random
import json

# Base JSON structure without placeholders
base_json = {
    "metadata": {
        "name": "",
        "namespace": "",
        "description": ""
    },
    "spec": {
        "type": "agent",
        "lifecycle": "",
        "owner": "",
        "access_level": "",
        "category": "",
        "url": "",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "output": {
            "type": "",
            "description": ""
        }
    }
}

domains = ["example.com", "company.com", "service.com", "platform.com", "business.com"]
categories = ["Finance", "Customer Support", "Weather", "Health", "E-commerce", "Education", "Technology", "Transport", "Media", "Sports", "Travel", "Clothing", "Logistics"]
property_names = [
    "symbol", "date", "currency", "amount", "location", "product_id", "transaction_id", "user_id", "timestamp",
    "language", "destination", "departure_time", "arrival_time", "seat_number", "flight_number", "hotel_name",
    "room_type", "check_in_date", "check_out_date", "clothing_size", "color", "material", "order_id", "delivery_date",
    "tracking_number", "support_ticket_id", "customer_name", "issue_type", "resolution_status"
]
property_types = ["string", "integer", "number", "boolean", "array", "object"]
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
output_types = ["string", "integer", "number", "boolean", "array", "object"]
output_descriptions = [
    "Output value for the requested data", "Result of the operation", "Boolean flag indicating success or failure",
    "Calculated amount based on the input data", "Status of the operation", "Summary of the processed information",
    "ID of the created resource", "Confirmation message for the user"
]

agents = []

# Generate 50 agents with varied data
for i in range(50):
    properties = {}
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
        
        if property_type == "array":
            # Define the type of items inside the array (random choice)
            item_type = random.choice(["string", "integer", "number", "boolean"])
            properties[property_name] = {
                "type": "array",
                "items": {
                    "type": item_type
                },
                "description": property_description
            }
        else:
            properties[property_name] = {
                "type": property_type,
                "description": property_description
            }

        if random.choice([True, False]):
            required_fields.append(property_name)

    # Copy base_json and set values for each agent
    agent_json = deepcopy(base_json)
    agent_json["metadata"]["name"] = f"agent-{i + 1}"
    agent_json["metadata"]["namespace"] = "sandbox" if i % 2 == 0 else "production"
    agent_json["metadata"]["description"] = f"Description for agent-{i + 1}"
    agent_json["spec"]["lifecycle"] = "experimental" if i % 2 == 0 else "stable"
    agent_json["spec"]["owner"] = f"owner{i + 1}@{domains[i % len(domains)]}"
    agent_json["spec"]["access_level"] = "PRIVATE" if i % 2 == 0 else "PUBLIC"
    agent_json["spec"]["category"] = categories[i % len(categories)]
    agent_json["spec"]["url"] = f"https://api.{domains[i % len(domains)]}/agent-{i + 1}"
    agent_json["spec"]["parameters"]["properties"] = properties
    agent_json["spec"]["parameters"]["required"] = required_fields
    agent_json["spec"]["output"]["type"] = random.choice(output_types)
    agent_json["spec"]["output"]["description"] = random.choice(output_descriptions)

    agents.append(agent_json)

# Write to JSON file
with open("agents.json", "w") as file:
    json.dump(agents, file, indent=4)

print("Generated agents.json with 50 varied agent specifications.")
