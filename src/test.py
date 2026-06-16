from g4f import models
from g4f.client import Client

client = Client()

try:
    print("Streaming response...")
    response = client.chat.completions.create(
        model=models.default,
        messages=[
            {
                "role": "user",
                "content": "Hello! Can you tell me what model you are? Be specific on what model you are.",
            }
        ],  # Minimax-2.5
        stream=True,  # Enable streaming
    )

    # Iterate through the stream chunks as they arrive
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    print()  # Print a newline at the very end

except Exception as e:
    print(f"\nAn error occurred while streaming: {e}")
