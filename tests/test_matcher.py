from app.services.nlp_extractor import parse_resume
from app.services.job_parser import parse_job
from app.services.matcher import match_profile

def test_graph_indirect_matches():
 p=parse_resume('Morgan Lee\nBuilt BERT text classification models using PyTorch.\n')
 j=parse_job('Senior ML Engineer\nKnowledge of NLP and Deep Learning required.')
 m=match_profile(p,j)
 assert any(x.status=='INDIRECT' for x in m)
