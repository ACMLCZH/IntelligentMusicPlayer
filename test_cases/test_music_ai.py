from music_ai.ai_clients import *

# Test AI clients with environment variable tokens.
def test_clients_environ():
    openai_client = OpenAIClient()
    openai_data = {
        "model": "gpt-3.5",
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
    except:
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
    except:
        return False

    return True

if __name__ == '__main__':
    assert test_clients_environ() == True