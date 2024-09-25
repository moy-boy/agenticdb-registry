from http import HTTPStatus
import unittest
import json
import warnings
from fastapi.testclient import TestClient
from unittest import IsolatedAsyncioTestCase

from app.server import create_app

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestResetDB(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.post_headers = {'Content-Type': 'application/json'}
        cls.get_headers = {'Accept': 'application/json'}
    def setUp(self):
        self.test_json = """[
    {
        "metadata": {
            "name": "agent-50",
            "namespace": "production",
            "description": "Description for agent-50"
        },
        "spec": {
            "type": "agent",
            "lifecycle": "stable",
            "owner": "owner50@business.com",
            "access_level": "PUBLIC",
            "category": "Travel",
            "url": "https://api.business.com/agent-50",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "description": "Color of the item"
                    },
                    "customer_name": {
                        "type": "integer",
                        "description": "The hotel name for the booking"
                    },
                    "date": {
                        "type": "boolean",
                        "description": "Type of issue reported"
                    },
                    "clothing_size": {
                        "type": "object",
                        "description": "Type of issue reported"
                    },
                    "transaction_id": {
                        "type": "object",
                        "description": "Check-in date at the hotel"
                    }
                },
                "required": [
                    "currency",
                    "transaction_id"
                ],
                "additionalProperties": false
            },
            "output": {
                "type": "object",
                "description": "Boolean flag indicating success or failure"
            }
        }
    }
]
        """

    def test_post_json(self):
        with TestClient(create_app()) as c:
            print(self.test_json)
            json_data = json.loads(self.test_json)
            # Assuming self.post_headers and self.get_headers are dictionaries
            merged_headers = {**self.post_headers, **self.get_headers}
            response = c.post("/agents", json=json_data, headers=merged_headers)
            self.assertEqual(HTTPStatus.OK, response.status_code)
            response_json = response.json()
            required_keys = {"metadata", "spec"}
            for agent in response_json:
                self.assertTrue(required_keys.issubset(agent.keys()))
                metadata = agent["metadata"]
                required_metadata_keys = {"id", "ratings_id"}
                self.assertTrue(required_metadata_keys.issubset(metadata.keys()))
                print(json.dumps(response_json, indent=2))


            response = c.delete("/collections")
            results = response.json()
            self.assertEqual(0, results['agents'])
            self.assertEqual(0, results['applications'])
            self.assertEqual(0, results['ratings'])

            query = "Which agents can help interview candidates?"
            response = c.get("/agents", params={"query": query}, headers=self.get_headers)
            self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, response.status_code)


if __name__ == "__main__":
    unittest.main()
