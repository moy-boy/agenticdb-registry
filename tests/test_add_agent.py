import unittest
import yaml
import json
import warnings
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.server import app, lifespan
from unittest import IsolatedAsyncioTestCase

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestAgentEndpoint(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        # Create a TestClient instance
        cls.app = FastAPI(lifespan=lifespan)
        cls.client = TestClient(app)
        # Ensure app state is initialized
        with cls.client as c:
            c.get("/")

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
          input:
            type: string
            description: Input description for financial-data-oracle
          output:
            type: string
            description: Output description for financial-data-oracle
        """

    def test_post_yaml(self):
        headers = {'Content-Type': 'application/x-yaml'}
        response = self.client.post("/agents", content=self.test_yaml, headers=headers)
        self.assertEqual(200, response.status_code)
        response_json = response.json()
        required_keys = {"original_content", "parsed_content", "agent_id", "ratings_manifest", "ratings_id"}
        self.assertTrue(required_keys.issubset(response_json.keys()))
        print(json.dumps(response_json, indent=2))

        query = "Which agents have a category of Natural Language?"
        response = self.client.get("/agents", params={"query": query})
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
