import unittest
import yaml
import warnings
from pathlib import Path
from fastapi.testclient import TestClient
from app.server import create_app
from unittest import IsolatedAsyncioTestCase

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestAddMultipleAgents(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        # Create a TestClient instance
        cls.post_headers = {'Content-Type': 'application/x-yaml'}
        cls.get_headers = {'Accept': 'application/x-yaml'}
        # Get the absolute path to the current script's directory
        script_dir = Path(__file__).resolve().parent

        # Define the relative path to your file within the 'data' folder
        cls.agent_test_file = script_dir / 'data' / 'agents.yaml'

    def test_post_yaml(self):
        with TestClient(create_app()) as c:
            with open(self.agent_test_file, "r") as file:
                agents_yaml = file.read()
                # Split the file content into individual YAML documents
                agents = list(yaml.safe_load_all(agents_yaml))
                for agent in agents:
                    # Serialize each agent back to a YAML string
                    agent_yaml = yaml.dump(agent)
                    response = c.post("/agents", content=agent_yaml, headers=self.post_headers)
                    self.assertEqual(200, response.status_code)
                    response_json = response.json()
                    required_keys = {"agent_manifest", "ratings_manifest"}
                    for response_agent in response_json:
                        self.assertTrue(required_keys.issubset(response_agent.keys()))

            query = "Which agents have a category of Customer Support?"
            response = c.get("/agents", params={"query": query}, headers=self.get_headers)
            self.assertEqual(response.status_code, 200)
            try:
                agents = list(yaml.safe_load_all(response.content))
                for agent in agents:
                    required_keys = {"metadata", "ratings", "spec"}
                    self.assertTrue(required_keys.issubset(agent.keys()))
                    print(yaml.safe_dump(agent))
            except yaml.YAMLError as e:
                self.fail(f"Failed to parse YAML: {str(e)}")


if __name__ == "__main__":
    unittest.main()
