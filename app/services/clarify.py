from app.schemas import EvidenceMatch,Clarification

def build_questions(matches:list[EvidenceMatch])->list[Clarification]:
 return [Clarification(id='Q'+m.requirement_id,requirement_id=m.requirement_id,question=m.question) for m in matches if m.question]
