import requests

class OllamaChatbot:
    def __init__(self, model='llama2:latest ', api_url='http://localhost:11434/api/chat'):
        self.model = model
        self.api_url = api_url
        self.messages = []

    def ask(self, user_input):
        self.messages.append({"role": "user", "content": user_input})

        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": False
        }

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            reply = response.json()['message']['content']
            self.messages.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"Error: {str(e)}"

    def get_history(self):
        return self.messages


