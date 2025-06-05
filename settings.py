from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    openai_api_key : str = Field(..., validation_alias="OPENAI_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()

if __name__ == "__main__":
    print(settings.openai_api_key)