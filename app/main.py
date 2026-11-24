import json,uuid,logging,os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI,UploadFile,File,Form,HTTPException,Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.db import Base,engine,get_db,SessionLocal
from app.models_db import StoredResume,StoredJob,StoredMatch,CareerEvidence
from app.schemas import CandidateProfile,JobProfile,JobFitAssessment
from app.services.extract_text import extract_text,ExtractionError
from app.services.preprocess import clean_text
from app.services.nlp_extractor import parse_resume
from app.services.job_parser import parse_job
from app.services.matcher import match_profile
from app.services.scorer import score_assessment
from app.config import settings
logging.basicConfig(level=logging.INFO);log=logging.getLogger('careerintel')
@asynccontextmanager
async def lifespan(app):
 Base.metadata.create_all(bind=engine)
 app.state.models={'status':'ready','sentence_transformers':False,'faiss':False,'spacy':False}
 try:
  import spacy
  try:spacy.load('en_core_web_sm');app.state.models['spacy']=True
  except OSError:app.state.models['spacy']=False
 except Exception:pass
 yield
app=FastAPI(title='CareerIntel API',version='1.0.0',lifespan=lifespan)
STATIC=Path(__file__).resolve().parents[1]/'static'
app.mount('/static',StaticFiles(directory=STATIC),name='static')
@app.get('/',response_class=HTMLResponse)
def home():return (STATIC/'index.html').read_text(encoding='utf8')
@app.get('/api/health')
def health():return {'status':'ok','models':getattr(app.state,'models',{'status':'loading'})}
@app.get('/api/config')
def config():return {'llm_provider':settings.llm_provider,'cloud_llm_active':settings.llm_provider in ('openai','anthropic'),'models':getattr(app.state,'models',{})}
@app.post('/api/resumes')
async def upload_resume(file:UploadFile=File(...),db:Session=Depends(get_db)):
 data=await file.read()
 if len(data)>settings.upload_limit_mb*1024*1024:raise HTTPException(413,detail={'error':'file_too_large','message':'Maximum upload size is 10 MB.'})
 try:text,method=extract_text(data,file.filename or 'resume.txt');text=clean_text(text)
 except ExtractionError as e:raise HTTPException(400,detail={'error':'extraction_error','message':str(e)})
 if not text.strip():raise HTTPException(400,detail={'error':'empty_file','message':'No readable text was found in this file.'})
 profile=parse_resume(text,file.filename);profile.meta.warnings.append(f'Text extraction: {method}.')
 rid=str(uuid.uuid4());db.add(StoredResume(id=rid,profile_json=profile.model_dump_json(),source_text=text));db.commit()
 return {'id':rid,'profile':profile.model_dump()}
@app.get('/api/resumes/{rid}')
def get_resume(rid:str,db:Session=Depends(get_db)):
 row=db.get(StoredResume,rid)
 if not row:raise HTTPException(404,detail={'error':'not_found','message':'Resume not found.'})
 return CandidateProfile.model_validate_json(row.profile_json)
@app.put('/api/resumes/{rid}')
def update_resume(rid:str,profile:CandidateProfile,db:Session=Depends(get_db)):
 row=db.get(StoredResume,rid)
 if not row:raise HTTPException(404,detail={'error':'not_found','message':'Resume not found.'})
 row.profile_json=profile.model_dump_json();db.commit();return profile
@app.post('/api/jobs')
async def create_job(text:str|None=Form(None),file:UploadFile|None=File(None),db:Session=Depends(get_db)):
 if file:
  data=await file.read()
  try:text,_=extract_text(data,file.filename or 'job.txt')
  except ExtractionError as e:raise HTTPException(400,detail={'error':'extraction_error','message':str(e)})
 if not text or not text.strip():raise HTTPException(400,detail={'error':'empty_job','message':'Provide a job description.'})
 job=parse_job(clean_text(text));jid=str(uuid.uuid4());db.add(StoredJob(id=jid,job_json=job.model_dump_json()));db.commit();return {'id':jid,'job':job.model_dump()}
def _assess(rid,jid,weights,db):
 rr=db.get(StoredResume,rid);jr=db.get(StoredJob,jid)
 if not rr or not jr:raise HTTPException(404,detail={'error':'not_found','message':'Resume or job not found.'})
 profile=CandidateProfile.model_validate_json(rr.profile_json);job=JobProfile.model_validate_json(jr.job_json)
 approved=[{'answer':e.answer,'requirement_id':e.requirement_id} for e in db.query(CareerEvidence).filter_by(resume_id=rid,status='approved').all()]
 matches=match_profile(profile,job,approved);mid=str(uuid.uuid4());a=score_assessment(profile,job,matches,weights,mid);a.resume_id=rid;a.job_id=jid
 db.add(StoredMatch(id=mid,assessment_json=a.model_dump_json()));db.commit();return a
@app.post('/api/match')
def match(payload:dict,db:Session=Depends(get_db)):
 return _assess(payload.get('resume_id',''),payload.get('job_id',''),payload.get('weights'),db).model_dump()
@app.get('/api/match/{mid}')
def get_match(mid:str,db:Session=Depends(get_db)):
 r=db.get(StoredMatch,mid)
 if not r:raise HTTPException(404,detail={'error':'not_found','message':'Assessment not found.'})
 return JobFitAssessment.model_validate_json(r.assessment_json)
@app.post('/api/match/{mid}/clarifications/{qid}')
def clarification(mid:str,qid:str,payload:dict,db:Session=Depends(get_db)):
 matchrow=db.get(StoredMatch,mid)
 if not matchrow:raise HTTPException(404,detail={'error':'not_found','message':'Assessment not found.'})
 a=JobFitAssessment.model_validate_json(matchrow.assessment_json);q=next((x for x in a.clarifications if x.id==qid),None)
 if not q:raise HTTPException(404,detail={'error':'not_found','message':'Question not found.'})
 action=payload.get('action');answer=(payload.get('answer') or '').strip()
 if action not in ('approve','reject','skip'):raise HTTPException(400,detail={'error':'invalid_action','message':'Action must be approve, reject or skip.'})
 q.answer=answer;q.status='approved' if action=='approve' else 'rejected' if action=='reject' else 'pending'
 if action in ('approve','reject'):
  db.add(CareerEvidence(id=str(uuid.uuid4()),resume_id=a.resume_id,requirement_id=q.requirement_id,answer=answer,status=q.status))
 matchrow.assessment_json=a.model_dump_json();db.commit();return {'status':q.status,'assessment':a.model_dump()}
@app.post('/api/match/{mid}/rescore')
def rescore(mid:str,db:Session=Depends(get_db)):
 old=get_match(mid,db);new=_assess(old.resume_id,old.job_id,old.weights,db)
 return {'before':old.overall_score,'after':new.overall_score,'assessment':new.model_dump()}
@app.get('/api/evidence')
def evidence(resume_id:str,db:Session=Depends(get_db)):
 return [dict(id=e.id,requirement_id=e.requirement_id,answer=e.answer,status=e.status,source=e.source) for e in db.query(CareerEvidence).filter_by(resume_id=resume_id).all()]
SAMPLE_RESUME='''ALEX MORGAN\nalex.morgan@example.com | +1 555 010 2040 | Seattle, WA\nSenior Machine Learning Engineer\nSUMMARY\nMachine learning engineer with 8 years of Python development and 5 years of Machine Learning building production predictive systems.\nEXPERIENCE\nSenior Machine Learning Engineer | Northstar Analytics\n2022 - Present\n- Led a team of 6 engineers delivering model deployment pipelines using AWS SageMaker and Python.\n- Built a BERT text classification platform with PyTorch, improving support routing accuracy by 31%.\n- Reduced model inference latency by 40% through optimized batching and monitoring.\nMachine Learning Engineer | Meridian Labs\n2019 - 2022\n- Developed predictive models with Python, PyTorch and scikit-learn for customer risk scoring.\n- Deployed scalable training workflows on AWS and SageMaker, reducing training costs by 22%.\n- Improved classification F1 score from 0.78 to 0.91 through feature engineering.\nPython Developer | BluePeak Systems\n2016 - 2019\n- Built Python services and PostgreSQL data pipelines processing 2 million records daily.\n- Mentored junior developers and coordinated delivery across a team of 6 engineers.\nEDUCATION\nMaster of Science in Computer Science, University of Washington, 2016\nACHIEVEMENTS\n- Reduced inference latency by 40% across production models.\n- Improved classification F1 score by 13 percentage points.\n- Reduced cloud training costs by 22%.\n- Processed 2 million records per day with 99.9% pipeline availability.\n'''
SAMPLE_JOB='''Senior Machine Learning Engineer\nWe are seeking a Senior Machine Learning Engineer.\nRequirements:\n- 5+ years Python development required.\n- 3+ years Machine Learning experience required.\n- Knowledge of NLP and Deep Learning required.\n- AWS experience required.\n- Experience leading technical projects required.\n- Master's degree preferred.\n'''
@app.post('/api/demo')
def demo(db:Session=Depends(get_db)):
 profile=parse_resume(SAMPLE_RESUME,'resume_sample.txt');rid=str(uuid.uuid4());job=parse_job(SAMPLE_JOB);jid=str(uuid.uuid4())
 db.add(StoredResume(id=rid,profile_json=profile.model_dump_json(),source_text=SAMPLE_RESUME));db.add(StoredJob(id=jid,job_json=job.model_dump_json()));db.commit()
 a=_assess(rid,jid,None,db);return {'resume_id':rid,'job_id':jid,'profile':profile.model_dump(),'job':job.model_dump(),'assessment':a.model_dump()}
