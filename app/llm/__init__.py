from app.config import settings
from app.llm.none_provider import NoneProvider

def get_provider():
 p=settings.llm_provider
 if p=='anthropic' and settings.anthropic_api_key:
  from app.llm.anthropic_provider import AnthropicProvider
  return AnthropicProvider(settings.anthropic_api_key,settings.llm_model)
 if p=='openai' and settings.openai_api_key:
  from app.llm.openai_provider import OpenAIProvider
  return OpenAIProvider(settings.openai_api_key,settings.llm_model)
 if p=='ollama':
  from app.llm.ollama_provider import OllamaProvider
  return OllamaProvider(settings.llm_model)
 return NoneProvider()
