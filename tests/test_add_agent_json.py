import unittest
import yaml
import json
import warnings
from fastapi.testclient import TestClient
from unittest import IsolatedAsyncioTestCase

from app.server import create_app

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestAddAgent(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.post_headers = {'Content-Type': 'application/json'}
        cls.get_headers = {'Accept': 'application/json'}
    def setUp(self):
        self.test_yaml = """
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
  parameters:
    type: object
    properties:
      symbol:
        type: string
        description: ticker symbol
      date:
        type: string
        description: A specific date in the format yyyy-mm-dd
      currency:
        type: string
        enum:
          - USD
          - JPY
        description: "the currency of the desired output value"
    required:
      - symbol
    additionalProperties: false
  output:
    type: float
    description: Output description for financial-data-oracle
        """

    def test_post_yaml(self):
        with TestClient(create_app()) as c:
            # Parse the YAML string
            print(self.test_yaml)
            yaml_data = yaml.safe_load(self.test_yaml)
            # Convert the parsed YAML data to JSON
            json_data = json.dumps(yaml_data, indent=2)
            response = c.post("/agents", content=json_data, headers=self.post_headers)
            self.assertEqual(200, response.status_code)
            response_json = response.json()
            required_keys = {"agent_manifest", "ratings_manifest"}
            for agent in response_json:
                self.assertTrue(required_keys.issubset(agent.keys()))
                metadata = agent["agent_manifest"]["metadata"]
                required_metadata_keys = {"id", "ratings_id"}
                self.assertTrue(required_metadata_keys.issubset(metadata.keys()))
                print(json.dumps(response_json, indent=2))

            query = "Which agents have a category of Natural Language?"
            response = c.get("/agents", params={"query": query}, headers=self.get_headers)
            self.assertEqual(200, response.status_code)
            response_json = response.json()
            agents_yaml = response_json["agents"]
            try:
                agents = list(yaml.safe_load_all(agents_yaml))
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
