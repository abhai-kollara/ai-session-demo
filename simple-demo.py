from anthropic import Anthropic

client = Anthropic()  # the library that talks to the model

messages = [{
    "role": "user",
    "content": "What is the weather like in Thrissur right now?",
}]

response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1024,  # the longest reply we allow
    messages=messages,
)
print(response.content[0].text)
