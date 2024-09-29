#llm.py is connected to app.py

from openai import OpenAI

# we haven't configured authentication, we pass a dummy value
openai_api_key = "EMPTY"
# modify this value to match your host, remember to add /v1 at the end
openai_api_base = "http://192.168.0.105:7182/v1"

client = OpenAI(
    api_key=openai_api_key, 
    base_url=openai_api_base,
)

class Chatbot:
    def __init__(self, api_key, base_url):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate_response(self, conversation_history, user_query):
        try:
            # Build a prompt using the conversation history
            conversation = "\n".join([f"You: {query}\nBot: {response}" for query, response in conversation_history])
            prompt = f"{conversation}\nYou: {user_query}\nBot:"

            completion = self.client.completions.create(
                model="google/gemma-2b-it",
                prompt=prompt,
                max_tokens=400,
                temperature=0.6,
                top_p=1.0,
                frequency_penalty=0.2,
                presence_penalty=0.1,
                
            )
            return completion.choices[0].text
        except Exception as e:
            return f"Error occurred: {str(e)}"