import requests


class OpenAIAgent:
    def __init__(self, api_key, organization_name):
        self.api_key = api_key
        self.organization_name = organization_name
        self.url = 'https://api.openai.com/v1/chat/completions'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        self.model = 'gpt-3.5-turbo'

    def chat(self, message):
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': f'This is a customer support agent for {self.organization_name}.'},
                {'role': 'user', 'content': message},
            ],
            'temperature': 0.7
        }
        response = requests.post(self.url, headers=self.headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f'Request failed with status code {response.status_code}'
