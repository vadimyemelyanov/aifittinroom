import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

# Vector DB Configuration
PERSIST_DIRECTORY = "db"

# S3 Configuration
AWS_REGION = "eu-central-1"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 