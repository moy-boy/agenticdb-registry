import unittest
import warnings
from unittest import IsolatedAsyncioTestCase
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

    def test_invoke_agent(self):
        headers = {'Content-Type': 'application/x-yaml'}
        response = self.client.post("/agents", content=self.test_yaml, headers=headers)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        required_keys = {"agent_manifest", "ratings_manifest"}
        self.assertTrue(required_keys.issubset(response_json.keys()))

        # Define a local function to mock RemoteRunnable invoke method using TestClient
        def mock_invoke(url, payload):
            headers = {'Content-Type': 'application/json'}
            response = self.client.post(url, json=payload, headers=headers)
            return response.json()

        joke_chain = RemoteRunnable(self.base_url + "/joke")  # Or any relevant endpoint
        joke_chain.invoke = lambda payload: mock_invoke("/joke/invoke", payload)  # Override the invoke method

        response = joke_chain.invoke({'input': {'topic': 'cats'}})
        self.assertIn("output", response)
        self.assertIsNotNone(response["output"]["content"])
        print(response["output"]["content"])


if __name__ == '__main__':
    unittest.main()
