from pydantic_settings import BaseSettings

class Config(BaseSettings):
    POSTGRES_URL: str
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False  
    FIREBASE_CONFIG: str

    class Config:
        env_file = ".env"

config = Config()