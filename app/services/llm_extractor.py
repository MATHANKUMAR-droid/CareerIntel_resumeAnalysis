"""Provider-neutral structured extraction adapter. Offline mode intentionally returns no extra claims."""
from app.llm import get_provider

def extract_json(prompt:str,schema_model):
 provider=get_provider()
 if provider.__class__.__name__=='NoneProvider':return {}
 errors=''
 for _ in range(3):
  try:
   result=provider.extract_json(prompt+'\n'+errors,schema_model.model_json_schema())
   return schema_model.model_validate(result).model_dump()
  except Exception as exc:errors='Validation or provider error: '+str(exc)+'. Return corrected strict JSON.'
 return {}
