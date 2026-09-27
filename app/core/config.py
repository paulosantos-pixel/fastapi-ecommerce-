from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    PROJECT_NAME: str = "FrutiMix API"
    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:5173"
    
    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

settings = Settings()