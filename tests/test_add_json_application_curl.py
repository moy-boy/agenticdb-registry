import json
import multiprocessing
import subprocess
import threading
import time
import unittest
import os

import uvicorn

from app.server import create_app

class CurlCommandTest(unittest.TestCase):

    # Get the base URL from the environment variable, use a default if not set
    base_url = os.getenv("BASE_API_URL", "http://127.0.0.1:8000")
    applications_url = f"{base_url}/applications"

     # Function to run the FastAPI app in a separate thread
    @classmethod
    def run_server(self):
        if self.base_url == "http://127.0.0.1:8000":
            print("Starting local server...")
            uvicorn.run(create_app(), host="0.0.0.0", port=8000, log_level="info")   

    @classmethod
    def setUpClass(cls):
        # Start the FastAPI server in a separate thread
        # Start the FastAPI server in a separate thread
        cls.server_process = multiprocessing.Process(target=cls.run_server)
        cls.server_process.start()
        
        # Give some time for the server to start up
        time.sleep(2)   

    def test_curl_applications(self):

        curl_command = [
            "curl", 
            "-X", "POST", 
            self.applications_url,  # Use the URL from the env variable
            "-H", "Content-Type: application/json",
            "-H", "Accept: application/json",
            "-d", '''
            [
                {
                    "metadata": {
                        "name": "Stock Price Charting Application",
                        "namespace": "production",
                        "description": "Provides access to daily open, high, low, close stock prices over time and the ability to generate charts for the requested data"
                    },
                    "spec": {
                        "type": "application",
                        "lifecycle": "dev",
                        "owner": "admin@company.com",
                        "access_level": "PUBLIC",
                        "category": "Finance",
                        "setup": {
                            "compose": {
                                "compose_url": "https://ipfs.filebase.io/ipfs/somehash",
                                "run_command": "gunzip docker-compose.yml.gz && docker compose -f ./docker-compose.yml up -d"
                            }
                        },
                        "url": "http://localhost:3000/agent",
                        "method": "POST",
                        "example": "http://localhost:3000/agent  'Content-Type':'application/json'  {'input':'what was the Nvidia close price on August 22nd 2024', 'thread':'nvidia'}",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "input": {
                                    "type": "string",
                                    "description": "natural language request for stock price data and charting of the data as required"
                                },
                                "thread": {
                                    "type": "string",
                                    "description": "thread context id for the request"
                                }
                            },
                            "required": [
                                "input"
                            ],
                            "additionalProperties": false
                        },
                        "output": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "the natural language response and the Final Answer to the request with a chart location if requested"
                                }
                            },
                            "description": "the answer to the request"
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

        applications = json.loads(stdout_output)

        self.assertIn("Stock Price Charting Application", applications[0]["metadata"]["name"])

    @classmethod
    def tearDownClass(cls):
        # Terminate the FastAPI server process
        cls.server_process.terminate()
        cls.server_process.join()  # Ensure the process has been cleaned up

if __name__ == '__main__':
    unittest.main()
