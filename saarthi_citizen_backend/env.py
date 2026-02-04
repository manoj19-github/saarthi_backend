import os
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """
    Load environment variables from .env file"""
    env = os.getenv("DJANGO_ENV","development")
    env_file = f'.env.{env}'
    
    # Get the base directory where manage.py is located 
    base_dir = Path(__file__).resolve().parent.parent
    env_path = base_dir / env_file
    if not env_path.exists():
        raise FileNotFoundError(
            f"Environment file '{env_file}' not found in {base_dir}."
            f"Please create one from the template found in '{base_dir}/.env.template'."
        )
    # Load the environment variables from the .env file
    load_dotenv(env_path)
    print(f"Loaded environment variables from {env_file}")
    return env
    