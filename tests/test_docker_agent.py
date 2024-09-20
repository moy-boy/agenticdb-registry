from http import HTTPStatus
import unittest
import json
import warnings
from fastapi.testclient import TestClient
from unittest import IsolatedAsyncioTestCase
import subprocess
import time
import requests

from app.server import create_app

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestAddAgent(IsolatedAsyncioTestCase):


    def run_docker_container(self):
        # Docker command to run the container
        docker_command = ["docker", "run", "-d", "-p", "8001:8001", "rapenno/fastapi_agent"]

        # Execute the Docker command
        print("Running Docker container...")
        container_id = subprocess.check_output(docker_command).decode().strip()
        print(f"Container ID: {container_id}")

        return container_id

    def check_container_status(self, container_id):
        # Docker command to check the container status
        status_command = ["docker", "inspect", "-f", "{{.State.Running}}", container_id]
        try:
            status = subprocess.check_output(status_command).decode().strip()
            return status == "true"
        except subprocess.CalledProcessError:
            return False

    def wait_for_service(self, url, timeout=60, interval=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print("Service is up and running!")
                    return response
            except requests.exceptions.RequestException:
                print(f"Service not yet ready. Retrying in {interval} seconds...")
                time.sleep(interval)
        raise TimeoutError("Service did not become ready in time.")

    def main_docker(self):
        # Run the Docker container
        container_id = self.run_docker_container()

        # Wait until the container is fully running
        while not self.check_container_status(container_id):
            print("Waiting for container to be running...")
            time.sleep(2)

        print(f"Container {container_id} is running.")

        # URL to send the request to
        url = "http://localhost:8001/items/5?q=somequery"

        # Wait for the service to be ready and send the request
        try:
            response = self.wait_for_service(url)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except TimeoutError as e:
            print(e)

        # Optional: Stop the Docker container after the request
        stop_command = ["docker", "stop", container_id]
        subprocess.run(stop_command)
        print(f"Container {container_id} stopped.")


    @classmethod
    def setUpClass(cls):
        cls.post_headers = {'Content-Type': 'application/json'}
        cls.get_headers = {'Accept': 'application/json'}
    def setUp(self):
        self.test_json = """
[
    {
        "metadata": {
            "name": "Inventory Agent",
            "namespace": "production",
            "description": "Keeps track of item ids"
        },
        "spec": {
            "type": "agent",
            "lifecycle": "stable",
            "owner": "owner50@business.com",
            "access_level": "PUBLIC",
            "category": "Travel",
            "setup": {
                "docker": {
                    "registry_url": "https://index.docker.io/v1/",
                    "image_name": "rapenno/fastapi_agent",
                    "image_tag": "latest",
                    "run_command": "docker run -d -p 8001:8001 rapenno/fastapi_agent"
                }
            },
            "url": "http://localhost:8001/items/{itemid}",
            "method": "GET",
            "example": "http://localhost:8001/items/5?q=somequery",
            "parameters": {
                "type": "object",
                "properties": {
                    "itemid": {
                        "type": "integer",
                        "description": "item number"
                    },
                    "query": {
                        "type": "string",
                        "description": "a query string"
                    }
                },
                "required": [
                    "itemid",
                    "query"
                ],
                "additionalProperties": false
            },
            "output": {
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "integer",
                        "description": "the item id"
                    },
                    "q": {
                        "type": "string",
                        "description": "query string"
                    }
                },
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
                spec = agent["spec"]
                required_spec_keys = {"setup", "example"}
                self.assertTrue(required_spec_keys.issubset(spec.keys()))
                print(json.dumps(response_json, indent=2))

            query = "Which agents can keep track of inventory?"
            response = c.get("/agents", params={"query": query}, headers=self.get_headers)
            self.assertEqual(HTTPStatus.OK, response.status_code)
            try:
                agents_json = response.json()
                for agent in agents_json:
                    required_keys = {"spec"}
                    self.assertTrue(required_keys.issubset(agent.keys()))
                    self.assertIn("setup", agent["spec"])
                    docker_info = agent["spec"]["setup"]["docker"]
                    print(json.dumps(docker_info))
                    self.main_docker()
            except Exception as e:
                self.fail(f"Failed to parse JSON: {str(e)}")


if __name__ == "__main__":
    unittest.main()
