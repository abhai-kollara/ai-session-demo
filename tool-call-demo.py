from anthropic import Anthropic

client = Anthropic()


# 1. A simple Python function to act as our tool
def get_weather(location: str) -> str:
  # Mocked weather database
  data = {
      "paris": "18 C and partly cloudy",
      "tokyo": "22 C and sunny",
      "san francisco": "14 C and foggy",
      "thrissur": "28 C and rainy"
  }
  
  return data.get(location.lower(), "weather information for the city is unavailable")


# 2. Schema telling Claude what the function does and what arguments it expects
tools = [{
    "name": "get_weather",
    "description": "Get the current weather conditions for a given city.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name, e.g. Paris, Tokyo",
            }
        },
        "required": ["location"],
    },
}]

# 3. User asks a question Claude can't answer without external data
messages = [
    {"role": "user", "content": "What is the weather like in Cochin right now?"}
]

# 4. Claude replies with a tool_use block instead of an answer
response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)
tool_use = next(block for block in response.content if block.type == "tool_use")
print(f"Claude wants to call {tool_use.name} with {tool_use.input}")

# 5. We run the function ourselves and hand the result back
output = get_weather(tool_use.input["location"])
messages.append({"role": "assistant", "content": response.content})
messages.append({
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": tool_use.id,
        "content": output,
    }],
})

# 6. Claude now has the data and writes the final answer
response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)
print(response.content[0].text)
