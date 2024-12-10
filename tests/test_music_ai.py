from music_ai.ai_clients import *
import os

# Test AI clients with environment variable tokens.
def test_clients_environ():
    openai_client = OpenAIClient(
        endpoint="https://models.inference.ai.azure.com",
    )
    openai_data = {
        "model": "gpt-4o-mini",
        "messages": [{
            "role": "system",
            "content": "You are a chatting robot."
        }, {
            "role": "user",
            "content": "Hello"
        }],
    }
    try:
        print(openai_client.request(openai_data))
        print("Passed!")
    except Exception as e:
        print(f"Fail to pass test case: {e}")
        return False
    
    suno_client = SunoAIClient()
    suno_data = {
        'action': 'generate',
        'prompt': "Make a happy song.",
        'model': 'chirp-v3-5',
        'custom': False,
        'instrumental': False,
    }
    try:
        print(suno_client.request(suno_data))
        print("Passed!")
    except Exception as e:
        print(f"Fail to pass test case: {e}")
        return False

    return True

if __name__ == '__main__':
    assert test_clients_environ() == True