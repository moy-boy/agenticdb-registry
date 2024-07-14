import unittest
import requests


class TestAgentEndpoint(unittest.TestCase):
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
        """

    def test_post_yaml(self):
        headers = {'Content-Type': 'application/x-yaml'}
        response = requests.post(f"{self.base_url}/agent", data=self.test_yaml, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("original_content", response.json())
        self.assertIn("parsed_content", response.json())


if __name__ == "__main__":
    unittest.main()
