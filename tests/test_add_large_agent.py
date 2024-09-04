import unittest
import yaml
import json
import warnings
from fastapi.testclient import TestClient
from unittest import IsolatedAsyncioTestCase

from  app.server import create_app

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestAddAgent(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.post_headers = {'Content-Type': 'application/x-yaml'}
        cls.get_headers = {'Accept': 'application/x-yaml'}

    def setUp(self):
        self.test_yaml = """
metadata:
  name: financial-data-oracle
  namespace: production
  description: |
    Description for agent financial-data-oracle
spec:
  type: agent
  lifecycle: stable
  owner: owner2@company.com
  access_level: PUBLIC
  category: Customer Support
  url: https://api.company.com/financial-data-oracle
  parameters:
    type: object
    properties:
      flight_number:
        type: boolean
        description: "Type of issue reported"
      issue_type:
        type: string
        description: "Ticker symbol for financial data"
      departure_time:
        type: float
        description: "Material of the product"
      product_id:
        type: string
        description: "Ticker symbol for financial data"
      symbol:
        type: float
        description: "Check-out date from the hotel"
    required:
      - issue_type
      - departure_time
      - product_id
      - symbol
    additionalProperties: false
  output:
    type: string
    description: ID of the created resource
        """

    def test_post_yaml(self):
        with TestClient(create_app()) as c:
            response = c.post("/agents", content=self.test_yaml, headers=self.post_headers)
            self.assertEqual(200, response.status_code)
            response_json = response.json()
            required_keys = {"agent_manifest", "ratings_manifest"}
            for agent in response_json:
                self.assertTrue(required_keys.issubset(agent.keys()))
                metadata = agent["agent_manifest"]["metadata"]
                required_metadata_keys = {"id", "ratings_id"}
                self.assertTrue(required_metadata_keys.issubset(metadata.keys()))
                print(json.dumps(response_json, indent=2))

            query = "Which agents have a category of Customer Support?"
            response = c.get("/agents", params={"query": query}, headers=self.get_headers)
            self.assertEqual(200, response.status_code)
            try:
                agents = list(yaml.safe_load_all(response.content))
                for agent in agents:
                    required_keys = {"metadata", "ratings", "spec"}
                    self.assertTrue(required_keys.issubset(agent.keys()))
                    self.assertIn("name", agent["metadata"])
                    self.assertIn("score", agent["ratings"]["data"])
                    self.assertEqual("financial-data-oracle", agent["metadata"]["name"])
                    print(yaml.safe_dump(agent))
            except yaml.YAMLError as e:
                self.fail(f"Failed to parse YAML: {str(e)}")


if __name__ == "__main__":
    unittest.main()
