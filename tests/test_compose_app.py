from http import HTTPStatus
import unittest
import json
import warnings
from fastapi.testclient import TestClient
from unittest import IsolatedAsyncioTestCase, SkipTest
import subprocess
import time
from pytest import skip
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
            "name": "Stock Price Application",
            "namespace": "production",
            "description": "Provides stock proce over time"
        },
        "spec": {
            "type": "application",
            "lifecycle": "dev",
            "owner": "owner50@business.com",
            "access_level": "PUBLIC",
            "category": "Finance",
            "setup": {
                "compose": {
                    "compose_url": "https://myurl.com/compose.yaml",
                    "run_command": "docker compose up --detach"
                }
            },
            "url": "http://localhost:8001/stock/",
            "method": "GET",
            "example": "http://localhost:8001/stock?query=CSCO",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "stock symbol such as CSCO"
                    }
                },
                "required": [
                    "query"
                ],
                "additionalProperties": false
            },
            "output": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "stock symbol such as CSCO"
                    },
                    "price": {
                        "type": "integer",
                        "description": "stock price"
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
            response = c.post("/applications", json=json_data, headers=merged_headers)
            self.assertEqual(HTTPStatus.OK, response.status_code)
            response_json = response.json()
            required_keys = {"metadata", "spec"}
            for application in response_json:
                self.assertTrue(required_keys.issubset(application.keys()))
                spec = application["spec"]
                required_spec_keys = {"setup", "example"}
                self.assertTrue(required_spec_keys.issubset(spec.keys()))
                self.assertIn("compose", spec["setup"])
                print(json.dumps(response_json, indent=2))

            query = "Which application can provide stock price?"
            response = c.get("/applications", params={"query": query}, headers=self.get_headers)
            self.assertEqual(HTTPStatus.OK, response.status_code)
            try:
                apps_json = response.json()
                for application in apps_json:
                    required_keys = {"spec"}
                    self.assertTrue(required_keys.issubset(application.keys()))
                    self.assertIn("type", application["spec"])
                    self.assertEqual("application", application["spec"]["type"])
                    self.assertIn("setup", application["spec"])
                    compose_info = application["spec"]["setup"]["compose"]
                    print(json.dumps(compose_info))
            except Exception as e:
                self.fail(f"Failed to parse JSON: {str(e)}")


if __name__ == "__main__":
    unittest.main()
