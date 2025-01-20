import openai
import os
import time
from typing import Optional
from openai import OpenAIError, APIError, RateLimitError, APIConnectionError

class OpenAIClient:
    def __init__(self, api_key: str):
        """Initialize the OpenAI client with your API key."""
        if not api_key:
            raise ValueError("API key cannot be empty")
        self.client = openai.Client(api_key=api_key)
    
    def create_chat_completion(
        self,
        messages: list,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Optional[str]:
        """
        Create a chat completion using OpenAI's models with error handling.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: The model to use (defaults to gpt-3.5-turbo)
            temperature: Controls randomness (0.0 to 1.0)
            max_retries: Maximum number of retry attempts for recoverable errors
            retry_delay: Delay between retries in seconds
        
        Returns:
            The generated response text, or None if all retries failed
            
        Raises:
            ValueError: If messages are empty or malformed
            Exception: For unrecoverable API errors
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")
        
        if not isinstance(messages, list):
            raise ValueError("Messages must be a list of dictionaries")
            
        for message in messages:
            if not isinstance(message, dict) or 'role' not in message or 'content' not in message:
                raise ValueError("Each message must be a dictionary with 'role' and 'content' keys")

        retries = 0
        while retries <= max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
                return response.choices[0].message.content

            except RateLimitError as e:
                if retries == max_retries:
                    print(f"Rate limit exceeded. Error: {str(e)}")
                    return None
                wait_time = retry_delay * (2 ** retries)  # Exponential backoff
                print(f"Rate limit reached. Waiting {wait_time} seconds...")
                time.sleep(wait_time)

            except APIConnectionError as e:
                if retries == max_retries:
                    print(f"Connection error: {str(e)}")
                    return None
                print(f"Connection error, retrying... ({retries + 1}/{max_retries})")
                time.sleep(retry_delay)

            except APIError as e:
                if retries == max_retries:
                    print(f"API error: {str(e)}")
                    return None
                print(f"API error, retrying... ({retries + 1}/{max_retries})")
                time.sleep(retry_delay)

            except OpenAIError as e:
                # Unrecoverable error
                print(f"OpenAI API error: {str(e)}")
                raise Exception(f"Unrecoverable error when calling OpenAI API: {str(e)}")

            except Exception as e:
                # Unexpected error
                print(f"Unexpected error: {str(e)}")
                raise

            retries += 1

        return None

def main():
    try:
        # Try to get API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Please set the OPENAI_API_KEY environment variable")
        
        client = OpenAIClient(api_key)
        
        # Example with default model (gpt-3.5-turbo)
        messages = [
            {"role": "user", "content": "What is the capital of France?"}
        ]
        
        response = client.create_chat_completion(messages)
        if response:
            print("GPT-3.5 Response:", response)
        else:
            print("Failed to get response after all retries")
        
    except ValueError as e:
        print(f"Configuration error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()