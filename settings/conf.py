from decouple import config


ENV_POSSIBLE_OPTIONS = ("local", "prod")

ENV_ID = config("DJANGORLAR_ENV_ID", cast=str)
SECRET_KEY = config("SECRET_KEY", cast=str)
