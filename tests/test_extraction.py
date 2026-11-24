from app.services.nlp_extractor import parse_resume

def test_extracts_evidence_and_entities():
 p=parse_resume('Taylor Smith\ntaylor@example.com\nPython developer with 8 years of Python.\nMaster of Science in Computer Science\nBuilt Python APIs improving latency by 30%.')
 assert p.candidate.email=='taylor@example.com'
 assert any(s.canonical_name=='Python' and s.evidence for s in p.skills)
 assert p.education and p.achievements

def test_missing_sections_and_non_english_text_are_safe():
 p=parse_resume('Jean Dupont\njean@example.fr\nDéveloppeur logiciel expérimenté.')
 assert p.candidate.email=='jean@example.fr'
 assert isinstance(p.skills,list)
