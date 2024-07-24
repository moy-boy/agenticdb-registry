import unittest
import yaml
import warnings
from fastapi.testclient import TestClient
from app.server import create_app
from unittest import IsolatedAsyncioTestCase

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestAddMultipleAgentsSingleRequest(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.headers = {'Content-Type': 'application/x-yaml'}

    def test_post_yaml(self):
        with TestClient(create_app()) as c:
            with open("data/agents.yaml", "r") as file:
                agents_yaml = file.read()
                response = c.post("/agents", content=agents_yaml, headers=self.headers)
                self.assertEqual(response.status_code, 200)
                response_json = response.json()
                required_keys = {"agent_manifest", "ratings_manifest"}
                for agent in response_json:
                    self.assertTrue(required_keys.issubset(agent.keys()))

            query = "Which agents have a category of Customer Support?"
            response = c.get("/agents", params={"query": query})
            self.assertEqual(response.status_code, 200)
            response_json = response.json()
            agents_yaml = response_json["agents"]
            try:
                agents = list(yaml.safe_load_all(agents_yaml))
                for agent in agents:
                    required_keys = {"metadata", "ratings", "spec"}
                    self.assertTrue(required_keys.issubset(agent.keys()))
                    print(yaml.safe_dump(agent))
            except yaml.YAMLError as e:
                self.fail(f"Failed to parse YAML: {str(e)}")


if __name__ == "__main__":
    unittest.main()
