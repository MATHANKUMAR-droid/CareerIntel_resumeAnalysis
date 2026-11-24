import re
from app.schemas import JobProfile,Requirement
from app.services.taxonomy import canonicalize

def parse_job(text:str)->JobProfile:
    lines=[x.strip(' -•') for x in text.splitlines() if x.strip()]
    title=next((x for x in lines if re.search(r'engineer|developer|analyst|scientist|manager|architect',x,re.I)),'Target role')
    req=[]; idx=0
    for term in ['Python','Machine Learning','NLP','Deep Learning','AWS','SQL','PostgreSQL','Leadership','PyTorch','BERT','Docker','Communication','Project Management']:
        m=re.search(re.escape(term),text,re.I)
        if m:
            line=next((ln for ln in lines if re.search(re.escape(term),ln,re.I) and re.search(r'\d+\s*\+?\s*years?',ln,re.I)),next((ln for ln in lines if re.search(re.escape(term),ln,re.I) and ln != title),next((ln for ln in lines if re.search(re.escape(term),ln,re.I)),lines[0])))
            around=line
            years=re.search(r'(\d+(?:\.\d+)?)\s*\+?\s*years?',line,re.I)
            mandatory=not bool(re.search(r'preferred|nice to have|plus|optional',line,re.I))
            idx+=1; req.append(Requirement(id=f'R{idx}',text=around[:220],type='skill',mandatory=mandatory,min_years=float(years.group(1)) if years else None,skill=canonicalize(term) or term,importance=3 if mandatory else 2))
    if re.search(r'master|M\.S\.|M\.Tech',text,re.I):
        idx+=1;req.append(Requirement(id=f'R{idx}',text='Master’s degree preferred',type='education',mandatory=False,skill='master',importance=2))
    if re.search(r'lead|manage|technical project',text,re.I):
        idx+=1;req.append(Requirement(id=f'R{idx}',text='Experience leading technical projects',type='responsibility',mandatory=True,skill='Leadership',importance=2))
    return JobProfile(title=title,requirements=req,raw_text=text)
