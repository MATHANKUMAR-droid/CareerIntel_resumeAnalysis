from app.services.nlp_extractor import parse_resume
from app.services.job_parser import parse_job
from app.services.matcher import match_profile
from app.services.scorer import score_assessment

def test_score_is_deterministic_and_weighted():
 p=parse_resume('Sam Dev\nPython developer with 8 years of Python.\nMaster of Science in Computer Science.')
 j=parse_job('Python developer 5+ years Python required. Masters preferred.')
 m=match_profile(p,j);a=score_assessment(p,j,m,assessment_id='same');b=score_assessment(p,j,m,assessment_id='same')
 assert a.overall_score==b.overall_score
 assert abs(sum(a.weights.values())-1)<1e-9
