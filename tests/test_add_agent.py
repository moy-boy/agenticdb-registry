import unittest
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
        response = self.client.post("/agent", content=self.test_yaml, headers=headers)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertIn("original_content", response_json)
        self.assertIn("parsed_content", response_json)
        self.assertIn("agent_id", response_json)


if __name__ == "__main__":
    unittest.main()
