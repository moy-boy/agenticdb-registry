import unittest
import warnings
import random
from unittest import IsolatedAsyncioTestCase

import yaml
from fastapi import FastAPI
from fastapi.testclient import TestClient
from langserve import RemoteRunnable
from app.server import app, lifespan

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestAgent(IsolatedAsyncioTestCase):

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
        self.test_agent_yaml = """
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
        self.ratings_yaml = f"""
        ratings:
          agent_id: placeholder_agent_id
          id: placeholder_some_id
          data:
            score: {random.randint(1, 5)}
        """

    def test_change_ratings(self):
        headers = {'Content-Type': 'application/x-yaml'}
        response = self.client.post("/agents", content=self.test_agent_yaml, headers=headers)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        required_keys = {"agent_manifest", "ratings_manifest"}
        self.assertTrue(required_keys.issubset(response_json.keys()))

        headers = {'Content-Type': 'application/x-yaml'}
        ratings_dict = yaml.safe_load(self.ratings_yaml)
        ratings_dict["ratings"]["agent_id"] = response_json["agent_manifest"]["metadata"]["id"]
        ratings_dict["ratings"]["id"] = response_json["agent_manifest"]["metadata"]["ratings_id"]
        updated_ratings_yaml = yaml.dump(ratings_dict)
        response = self.client.post("/ratings", content=updated_ratings_yaml, headers=headers)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(ratings_dict["ratings"]["data"]["score"], response_json["ratings"]["data"]["score"])
        response = self.client.get("/ratings", params={"ratings_id": ratings_dict["ratings"]["id"]})
        self.assertEqual(200, response.status_code)
        response_json = response.json()
        self.assertEqual(ratings_dict["ratings"]["data"]["score"], response_json["data"]["score"])
        self.assertEqual(ratings_dict["ratings"]["id"], response_json["id"])
        print(response.content.decode("utf-8"))


if __name__ == '__main__':
    unittest.main()
