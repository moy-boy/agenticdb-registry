import json
import multiprocessing
import os
import subprocess
import threading
import time
import unittest

import uvicorn

from app.server import create_app

class CurlCommandTest(unittest.TestCase):


    base_url = os.getenv("BASE_API_URL", "http://127.0.0.1:8000")
    agents_url = f"{base_url}/agents"

    # Function to run the FastAPI app in a separate thread
    @classmethod
    def run_server(self):
        if self.base_url == "http://127.0.0.1:8000":
            print("Starting local server...")
            uvicorn.run(create_app(), host="0.0.0.0", port=8000, log_level="info")   

    @classmethod
    def setUpClass(cls):
        # Start the FastAPI server in a separate thread
        cls.server_process = multiprocessing.Process(target=cls.run_server)
        cls.server_process.start()
        
        # Give some time for the server to start up
        time.sleep(2)

    def test_curl_command(self):
        curl_command = [
            "curl", 
            "-X", "POST", 
            self.agents_url,  # Use the URL from the env variable,
            "-H", "Content-Type: application/json",
            "-H", "Accept: application/json",
            "-d", '''
            [
                {
                    "metadata": {
                        "name": "code-gen-chart-agent",
                        "namespace": "agents",
                        "description": "Requests for a javascript code generator to plot a chart with supplied free-form data."
                    },
                    "spec": {
                        "type": "agent",
                        "lifecycle": "dev",
                        "owner": "admin@company.com",
                        "access_level": "Public",
                        "category": "Natural Language",
                        "url": "https://api.example.com/code-gen-chart-agent/agent",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string",
                                    "description": "The request message for the chart code generator agent."
                                },
                                "thread": {
                                    "type": "string",
                                    "description": "The id to separate parallel message threads."
                                }
                            },
                            "required": ["message", "thread"],
                            "additionalProperties": false
                        },
                        "output": {
                            "type": "string",
                            "description": "The result of request, including any generated image location."
                        }
                    }
                }
            ]
            '''
        ]

        # Use subprocess to run the curl command
        result = subprocess.run(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Capture the stdout and stderr
        stdout_output = result.stdout
        stderr_output = result.stderr

        # Check if the command was successful
        self.assertEqual(result.returncode, 0, f"Curl command failed with error: {stderr_output}")

        # Output captured from stdout
        print(f"Command Output: {stdout_output}")

        agents = json.loads(stdout_output)
        self.assertIn("code-gen-chart-agent", agents[0]["metadata"]["name"])


    @classmethod
    def tearDownClass(cls):
        # Terminate the FastAPI server process
        cls.server_process.terminate()
        cls.server_process.join()  # Ensure the process has been cleaned up

if __name__ == '__main__':
    unittest.main()
