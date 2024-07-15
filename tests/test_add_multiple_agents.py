import unittest
import yaml
import json
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.server import app, lifespan
from unittest import IsolatedAsyncioTestCase


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
        self.base_url = "http://127.0.0.1:8000"

    def test_post_yaml(self):
        headers = {'Content-Type': 'application/x-yaml'}
        with open("data/agents.yaml", "r") as file:
            agents_yaml = file.read()
            # Split the file content into individual YAML documents
            agents = list(yaml.safe_load_all(agents_yaml))
            for agent in agents:
                # Serialize each agent back to a YAML string
                agent_yaml = yaml.dump(agent)
                response = self.client.post("/agents", content=agent_yaml, headers=headers)
                self.assertEqual(response.status_code, 200)
                response_json = response.json()
                self.assertIn("original_content", response_json)
                self.assertIn("parsed_content", response_json)
                self.assertIn("agent_id", response_json)

        query = "Which agents have a category of Customer Support?"
        response = self.client.get("/agents", params={"query": query})
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        agents_yaml = response_json["agents"]
        try:
            agents = list(yaml.safe_load_all(agents_yaml))
            for agent in agents:
                self.assertIn("name", agent["metadata"])
                print(yaml.safe_dump(agent))
        except yaml.YAMLError as e:
            self.fail(f"Failed to parse YAML: {str(e)}")


if __name__ == "__main__":
    unittest.main()
