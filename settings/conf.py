# Project modules
import os
from decouple import Config, RepositoryEnv

# --- Locate .env ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(BASE_DIR, '.env')

print(f"Looking for .env file at: {env_file}")
print(f"File exists: {os.path.exists(env_file)}")

# --- Load environment variables from .env ---
conf = Config(RepositoryEnv(env_file))

# --- Env id ---
ENV_POSSIBLE_OPTIONS = (
    "local",
    "prod",
)
ENV_ID = conf("DJANGORLAR_ENV_ID", cast=str)
SECRET_KEY = conf("SECRET_KEY", cast=str)
