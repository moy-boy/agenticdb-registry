from http import HTTPStatus
import unittest
import yaml
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
            response = c.post("/agents", content=self.test_yaml, headers=self.post_headers)
            self.assertEqual(HTTPStatus.OK, response.status_code)
            agents = list(yaml.safe_load_all(response.content))
            required_keys = {"metadata", "spec"}
            for agent in agents:
                self.assertTrue(required_keys.issubset(agent.keys()))
                metadata = agent["metadata"]
                required_metadata_keys = {"id", "ratings_id"}
                self.assertTrue(required_metadata_keys.issubset(metadata.keys()))
                print(yaml.safe_dump(agent, indent=2))

            query = "Which agents have a category of Natural Language?"
            response = c.get("/agents", params={"query": query}, headers=self.get_headers)
            self.assertEqual(HTTPStatus.OK, response.status_code)
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
