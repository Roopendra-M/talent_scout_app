import toml
import os

# Load secrets.toml
secrets = toml.load(".streamlit/secrets.toml")

# Access your Hugging Face token
HF_TOKEN = secrets.get("HUGGINGFACE_API_TOKEN")

# Set it as an environment variable (optional)
os.environ["HF_TOKEN"] = HF_TOKEN

print("Hugging Face Token:", HF_TOKEN)
