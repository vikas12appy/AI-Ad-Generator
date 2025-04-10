import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=api_key)

# List available models
print("Available Gemini models:")
for model in genai.list_models():
    print(f"- {model.name}")
    # Print model details
    print(f"  Display name: {model.display_name}")
    print(f"  Description: {model.description}")
    print() 