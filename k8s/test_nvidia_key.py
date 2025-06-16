from openai import OpenAI
import sys

def test_nvidia_api():
    try:
        # Initialize the client with the new API key
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key="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"
        )
        
        print("Client initialized successfully!")
        
        # Test with a simple completion
        completion = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": "Hello, are you working?"}],
            temperature=0.2,
            top_p=0.7,
            max_tokens=10
        )
        
        print(f"Response: {completion.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_nvidia_api()
    sys.exit(0 if success else 1)