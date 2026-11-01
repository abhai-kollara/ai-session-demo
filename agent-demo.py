from anthropic import Anthropic

client = Anthropic()


# 1. Two plain Python functions to act as our tools
def get_current_location() -> str:
  # Mocked GPS lookup
  return "Thrissur"


def get_weather(location: str) -> str:
  # Mocked weather database
  data = {
      "paris": "18 C and partly cloudy",
      "tokyo": "22 C and sunny",
      "san francisco": "14 C and foggy",
      "thrissur": "32 C and sunny"
  }
  return data.get(location.lower(), "weather information for the city is unavailable")


# 2. Schemas telling Claude what each tool does and what arguments it expects
tools = [
    {
        "name": "get_current_location",
        "description": "Get the city the user is currently in.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
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
    },
]

# 3. Map tool names to functions, so the loop below never needs to change
TOOL_FUNCTIONS = {
    "get_current_location": get_current_location,
    "get_weather": get_weather,
}

# 4. A question that needs two tool calls in the right order.
#    Nothing in this file says which order - Claude works that out.
messages = [
    {"role": "user", "content": "How is the weather here ?"}
]

# 5. The agent loop: keep going until Claude stops asking for tools
step = 0
while True:
  step += 1
  response = client.messages.create(
      model="claude-haiku-5-5",
      max_tokens=1024,
      tools=tools,
      messages=messages,
  )
  messages.append({"role": "assistant", "content": response.content})

  # Claude gave a final answer instead of a tool call - we are done
  if response.stop_reason != "tool_use":
    break

  # Run every tool Claude asked for and send the results back
  tool_results = []
  for block in response.content:
    if block.type == "tool_use":
      output = TOOL_FUNCTIONS[block.name](**block.input)
      print(f"Step {step}: Claude calls {block.name}({block.input}) -> {output}")
      tool_results.append({
          "type": "tool_result",
          "tool_use_id": block.id,
          "content": output,
      })
  messages.append({"role": "user", "content": tool_results})

# 6. Print the final answer
print(f"Step {step}: Claude answers")
print(response.content[0].text)
