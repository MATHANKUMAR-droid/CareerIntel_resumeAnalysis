from fastapi.testclient import TestClient
from app.main import app

def test_demo_flow():
 with TestClient(app) as c:
  r=c.post('/api/demo');assert r.status_code==200,r.text
  d=r.json();assert d['assessment']['overall_score']>0
  assert c.get('/api/health').json()['status']=='ok'

def test_clarification_persists_and_rescores():
 with TestClient(app) as c:
  d=c.post('/api/demo').json();a=d['assessment'];before=a['overall_score'];q=a['clarifications'][0]
  approved=c.post(f"/api/match/{a['id']}/clarifications/{q['id']}",json={'answer':'I used NLP for text classification for 3 years in production projects.','action':'approve'})
  assert approved.status_code==200
  assert len(c.get('/api/evidence',params={'resume_id':d['resume_id']}).json())==1
  result=c.post(f"/api/match/{a['id']}/rescore").json()
  assert result['after']>before
  again=c.post('/api/match',json={'resume_id':d['resume_id'],'job_id':d['job_id']}).json()
  assert next(x for x in again['requirements'] if x['requirement_id']==q['requirement_id'])['status']=='MET'

def test_empty_and_oversize_uploads():
 with TestClient(app) as c:
  empty=c.post('/api/resumes',files={'file':('empty.txt',b'')})
  assert empty.status_code==400
  huge=c.post('/api/resumes',files={'file':('huge.txt',b'x'*(10*1024*1024+1))})
  assert huge.status_code==413
