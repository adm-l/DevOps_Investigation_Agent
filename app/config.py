from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "devops-investigation-agent"
    app_env: str = "local"
    log_level: str = "INFO"
    api_key: str = Field(default="change-this-local-key", min_length=16)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"
    ollama_timeout_seconds: float = Field(default=90, gt=0, le=300)
    mcp_tool_timeout_seconds: float = Field(default=20, gt=0, le=120)
    agent_max_steps: int = Field(default=8, ge=1, le=20)
    agent_max_parallel_tools: int = Field(default=4, ge=1, le=16)
    rate_limit_requests: int = Field(default=30, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)
    @property
    def ollama_chat_url(self) -> str:
        return f"{self.ollama_base_url.rstrip('/')}/api/chat"

@lru_cache
def get_settings() -> Settings:
    return Settings()
