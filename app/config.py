import os
from dataclasses import dataclass
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
@dataclass
class Settings:
    database_url: str | None = os.getenv('DATABASE_URL')
    llm_provider: str = os.getenv('LLM_PROVIDER', 'none').lower()
    llm_model: str | None = os.getenv('LLM_MODEL')
    anthropic_api_key: str | None = os.getenv('ANTHROPIC_API_KEY')
    openai_api_key: str | None = os.getenv('OPENAI_API_KEY')
    upload_limit_mb: int = int(os.getenv('UPLOAD_LIMIT_MB', '10'))
settings = Settings()
