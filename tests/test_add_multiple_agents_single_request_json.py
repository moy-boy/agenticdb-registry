import unittest
import json
import warnings
from pathlib import Path
from fastapi.testclient import TestClient
from app.server import create_app
from unittest import IsolatedAsyncioTestCase

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestAddMultipleAgentsSingleRequest(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.post_headers = {'Content-Type': 'application/json'}
        cls.get_headers = {'Accept': 'application/json'}
        # Get the absolute path to the current script's directory
        script_dir = Path(__file__).resolve().parent

        # Define the relative path to your file within the 'data' folder
        cls.agent_test_file = script_dir / 'data' / 'agents.json'        

    def test_post_yaml(self):
        with TestClient(create_app()) as c:
            with open(self.agent_test_file, "r") as file:
                json_data = json.load(file)
                response = c.post("/agents", json=json_data, headers=self.post_headers)
                self.assertEqual(response.status_code, 200)
                response_json = response.json()
                required_keys = {"agent_manifest", "ratings_manifest"}
                for agent in response_json:
                    self.assertTrue(required_keys.issubset(agent.keys()))

            query = "Which agents have a category of Customer Support?"
            response = c.get("/agents", params={"query": query}, headers=self.get_headers)
            self.assertEqual(response.status_code, 200)
            try:
                agents = response.json()
                self.assertEqual(10, len(agents))
                for agent in agents:
                    required_keys = {"metadata", "ratings", "spec"}
                    self.assertTrue(required_keys.issubset(agent.keys()))
                    print(json.dumps(agent))
            except Exception as e:
                self.fail(f"Failed to parse YAML: {str(e)}")


if __name__ == "__main__":
    unittest.main()
