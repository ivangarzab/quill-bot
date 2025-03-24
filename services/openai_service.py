"""
Service for interfacing with OpenAI's API
"""

class OpenAIService:
    """Wrapper for OpenAI client to handle API interactions"""
    
    def __init__(self, api_key):
        """
        Initialize the OpenAI service
        
        Args:
            api_key (str): The OpenAI API key
        """
        from airobot import OpenAIClient
        self.api_key = api_key
        self.client = OpenAIClient(api_key)
    
    async def get_response(self, prompt):
        """
        Get a response from OpenAI for the given prompt with improved error handling
        
        Args:
            prompt (str): The prompt to send to OpenAI
                
        Returns:
            str: The response from OpenAI or error message
        """
        print(f"Fetching OpenAI response for prompt: {prompt}")
        try:
            messages = [
                {"role": "user", "content": f"{prompt}"}
            ]
            response = self.client.create_chat_completion(messages)
            if response:
                print("GPT-3.5 Response:", response)
                return response
            else:
                print("Failed to get response after all retries")
                return "I couldn't generate a response at this time. Please try again later."
        except ValueError as e:
            print(f"Configuration error: {str(e)}")
            return "I'm having trouble accessing my AI services right now."
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return "I encountered an error while processing your request."