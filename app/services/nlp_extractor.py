import re
from app.schemas import *
from app.services.taxonomy import canonicalize
from app.services.experience_calc import calculate_totals

SKILL_TERMS=['Python','Machine Learning','PyTorch','BERT','AWS','AWS SageMaker','SQL','PostgreSQL','TensorFlow','scikit-learn','Docker','Kubernetes','FastAPI','React','Java','C++','Git','Linux','Pandas','NumPy','Power BI','Tableau','Deep Learning','NLP','Natural Language Processing','Leadership','Project Management','Communication']

def parse_resume(text:str, source_file:str|None=None)->CandidateProfile:
    lines=[x.strip(' -•\t') for x in text.splitlines() if x.strip()]
    email=re.search(r'[\w.+-]+@[\w.-]+\.\w+',text); phone=re.search(r'(?:\+?\d[\d\s().-]{7,}\d)',text)
    name=next((x for x in lines[:5] if len(x.split()) in (2,3) and not '@' in x and not re.search(r'resume|curriculum|profile',x,re.I)),None)
    skills=[]; seen=set()
    for term in SKILL_TERMS:
        m=re.search(re.escape(term),text,re.I)
        can=canonicalize(term) or term
        if m and can.lower() not in seen:
            seen.add(can.lower()); quote=text[max(0,m.start()-45):min(len(text),m.end()+65)].replace('\n',' ').strip()
            skills.append(Skill(name=term,canonical_name=can,category='technical' if can not in ['Leadership','Project Management','Communication'] else 'soft',source='explicit',evidence=quote,confidence=.78))
    # Capture explicit tenure per canonical skill (e.g. '8 years of Python', '5 years ML').
    explicit_tenure={}
    for s in skills:
        patterns=[rf'(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?{re.escape(s.name)}',
                  rf'{re.escape(s.name)}\s+(?:for\s+)?(\d+(?:\.\d+)?)\s*\+?\s*years?']
        for pat in patterns:
            mt=re.search(pat,text,re.I)
            if mt:
                # Pattern two places the numeric group first as well.
                explicit_tenure[s.canonical_name]=max(explicit_tenure.get(s.canonical_name,0),float(mt.group(1)))
    for s in skills:
        if s.canonical_name in explicit_tenure:s.years_experience=explicit_tenure[s.canonical_name]
    years=re.search(r'(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?([\w+#. -]+)',text,re.I)
    exp=[]
    # Parse role blocks based on date ranges and nearby title/company lines.
    date_matches=list(re.finditer(r'((?:19|20)\d{2})\s*[-–]\s*((?:19|20)\d{2}|present)',text,re.I))
    for i,m in enumerate(date_matches[:8]):
        start=f'{m.group(1)}-01'; end='present' if m.group(2).lower()=='present' else f'{m.group(2)}-12'
        before=text[max(0,m.start()-180):m.start()].strip().splitlines()
        title=(before[-1].strip(' -') if before else 'Professional role')[:100]
        block=text[m.end():date_matches[i+1].start() if i+1<len(date_matches) else len(text)]
        bullets=[x.strip(' -•') for x in block.splitlines() if len(x.strip())>30][:8]
        tech=[s.canonical_name for s in skills if re.search(re.escape(s.name),block,re.I)]
        lead=bool(re.search(r'led|managed|mentored|team lead|headed|team of \d+',block,re.I))
        team=re.search(r'team of\s+(\d+)',block,re.I)
        resp=[Responsibility(text=b,evidence=b,skills_used=[s for s in tech if re.search(re.escape(s),b,re.I)],confidence=.72) for b in bullets]
        exp.append(Experience(title=title,company=None,start_date=start,end_date=end,is_leadership=lead,team_size=int(team.group(1)) if team else None,responsibilities=resp,technologies=tech))
    edu=[]
    for line in lines:
        if re.search(r'master|bachelor|ph\.d|doctor|diploma|M\.Tech|B\.Tech|M\.S\.',line,re.I):
            level='master' if re.search(r'master|M\.Tech|M\.S\.',line,re.I) else 'phd' if re.search(r'ph\.d|doctor',line,re.I) else 'bachelor' if re.search(r'bachelor|B\.Tech',line,re.I) else 'diploma'
            edu.append(Education(degree=line,level=level,field='Computer Science' if re.search(r'computer science',line,re.I) else None,evidence=line,confidence=.82))
    achievements=[]
    for line in lines:
        if re.search(r'\d+\s*%|\$\s?\d|\d+x|reduced|increased|improved|delivered',line,re.I):
            metric=re.search(r'\d+\s*%|\d+x|\$\s?[\d,.]+',line)
            achievements.append(Achievement(text=line,metric=metric.group(0) if metric else None,impact_category='performance' if re.search(r'latency|speed|performance',line,re.I) else 'quality',evidence=line,confidence=.8))
    summary=' '.join(lines[:2])[:500]
    totals=calculate_totals(exp,skills)
    # Surface role-derived skill tenure on each skill while retaining explicit tenure as a lower bound.
    for skill in skills:
        computed=totals['per_skill_years'].get(skill.canonical_name,0)
        skill.years_experience=max(skill.years_experience or 0,computed) or None
    # Explicit tenure statements are authoritative lower bounds.
    if explicit_tenure:
        for term,n in explicit_tenure.items():totals['per_skill_years'][term]=max(totals['per_skill_years'].get(term,0),n)
        totals['total_experience_years']=max(totals['total_experience_years'],max(explicit_tenure.values()))
    return CandidateProfile(candidate=Candidate(name=name,email=email.group(0) if email else None,phone=phone.group(0) if phone else None),summary=summary,skills=skills,experience=exp,education=edu,achievements=achievements,totals=Totals(**totals),meta=Meta(source_file=source_file,extraction_method='nlp_only',overall_confidence=.72,warnings=[] if skills else ['No known taxonomy skills detected.']))
