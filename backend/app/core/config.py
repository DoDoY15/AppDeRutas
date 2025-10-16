from pydantic import BaseSettings

class Settings(BaseSettings):
    Secret_Key: str = "your_secret_key"
    Algorithm: str = "HS256"
    Access_Token_Expire_Minutes: int = 30

Settings = Settings()