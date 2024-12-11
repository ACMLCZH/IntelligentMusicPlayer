import os
import requests
import openai
from typing import Dict


class SunoAIClient:
    def __init__(self, token=None):
        if token is None:
            token = os.environ["SUNOAI_TOKEN"]
        self.url = "https://api.acedata.cloud/suno/audios"
        self.headers = {
            "authorization": f"Bearer {token}",
            "accept": "application/json",
            "content-type": "application/json",
        }

    def request(self, data: Dict) -> Dict:
        response = requests.post(self.url, headers=self.headers, json=data, timeout=150)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.text}")
        return response.json()


suno_client = SunoAIClient()


"""
OpenAI
"""


class OpenAIClient:
    def __init__(self, api_key=None, endpoint=None):
        if api_key is None:
            api_key = os.environ["OPENAI_API_KEY"]

        openai_config = {"api_key": api_key}
        if endpoint is not None:
            openai_config["base_url"] = endpoint

        self.client = openai.OpenAI(**openai_config)

    def request(self, data: Dict) -> str:
        response = self.client.chat.completions.create(**data)
        return response.choices[0].message.content


openai_client = OpenAIClient(endpoint="https://models.inference.ai.azure.com")
