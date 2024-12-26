import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API Key
API_KEY = os.getenv("API_KEY")  # Retrieves the API key from the .env file

# Optionally, you can define headers or additional configurations here
HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}
