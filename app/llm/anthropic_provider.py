class AnthropicProvider:
 def __init__(self,key,model):self.key,self.model=key,model
 def extract_json(self,prompt,schema):
  import anthropic,json
  client=anthropic.Anthropic(api_key=self.key)
  r=client.messages.create(model=self.model or 'claude-sonnet-4-5',max_tokens=3000,messages=[{'role':'user','content':prompt+' Return strict JSON only.'}])
  return json.loads(r.content[0].text)
