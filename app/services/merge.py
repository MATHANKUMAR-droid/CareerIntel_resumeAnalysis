"""Evidence verification helpers used when combining model and deterministic extraction."""
try:
    from rapidfuzz import fuzz
except Exception:
    from difflib import SequenceMatcher
    class _Fuzz:
        @staticmethod
        def partial_ratio(a,b):
            return 100*SequenceMatcher(None,a,b).ratio()
    fuzz=_Fuzz()

def verify_quote(quote:str,source_text:str)->tuple[bool,float]:
 if not quote:return False,0.0
 score=fuzz.partial_ratio(quote.casefold(),source_text.casefold())/100
 return score>=.88,score

def merge_items(nlp_items:list[dict],llm_items:list[dict],source_text:str)->list[dict]:
 merged={}
 for item in [*nlp_items,*llm_items]:
  key=(item.get('canonical_name') or item.get('name') or item.get('text','')).casefold()
  if not key:continue
  verified,sim=verify_quote(item.get('evidence',''),source_text)
  item=dict(item);item['confidence']=float(item.get('confidence',.5))*(1 if verified else .4)
  if not verified:item.setdefault('flags',[]).append('unverified')
  item['evidence_verified']=verified
  if key not in merged or item['confidence']>merged[key]['confidence']:merged[key]=item
 return list(merged.values())
