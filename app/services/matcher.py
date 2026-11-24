import re,math
from app.schemas import *
from app.services.taxonomy import canonicalize,path_between

def match_profile(profile:CandidateProfile,job:JobProfile,approved:list[dict]|None=None)->list[EvidenceMatch]:
    approved=approved or []; found=[]
    skillmap={s.canonical_name.lower():s for s in profile.skills}
    for a in approved:
        n=canonicalize(a.get('answer',''))
        if n:skillmap[n.lower()]=Skill(name=n,canonical_name=n,category='verified',source='explicit',evidence=a['answer'],confidence=1.0,flags=['user-verified'])
    for r in job.requirements:
        evidence=[]; path=[]; sim=0.; graph=0.; score=0.; status='MISSING'; conf=.55; reason='No sufficiently relevant evidence found.'
        if r.type=='education':
            ok=any(e.level in ('master','phd') for e in profile.education)
            if ok:status='MET';score=.95;conf=.85;reason='A postgraduate degree is present in the education history.'
        elif r.type=='responsibility':
            for e in profile.experience:
                for b in e.responsibilities:
                    if re.search(r'lead|manage|mentor|team|project',b.text,re.I):evidence.append({'quote':b.evidence,'source':'experience responsibility'});sim=max(sim,.83)
            if evidence or any(e.is_leadership for e in profile.experience):status='MET';score=.9;conf=.82;reason='Leadership or technical project ownership is evidenced in role history.'
        else:
            target=(r.skill or r.text).lower(); candidate=skillmap.get(target)
            if candidate:
                evidence.append({'quote':candidate.evidence,'source':'skill','confidence':candidate.confidence})
                yrs=candidate.years_experience or profile.totals.per_skill_years.get(candidate.canonical_name,0)
                if r.min_years and yrs and yrs<r.min_years:status='PARTIAL';score=.68;reason=f'{candidate.canonical_name} is evidenced, but {yrs:g} years is below the {r.min_years:g}-year target.'
                else:status='MET';score=.94;reason=f'Direct verified resume evidence for {candidate.canonical_name}.'
                conf=candidate.confidence
            else:
                for have,s in skillmap.items():
                    p=path_between(s.canonical_name,r.skill or '')
                    if p and len(p)>1:
                        path=p;evidence.append({'quote':s.evidence,'source':'related skill','confidence':s.confidence});sim=.59;graph=.75;status='INDIRECT';score=.62;conf=.72
                        reason='Inferred through taxonomy relation: '+' → '.join(p)+'.';break
                if status=='MISSING':
                    # Similarity fallback based on meaningful token overlap.
                    tokens=set(re.findall(r'[a-z+#]{3,}',target));
                    for s in profile.skills:
                        overlap=tokens & set(re.findall(r'[a-z+#]{3,}',s.canonical_name.lower()))
                        if overlap:sim=max(sim,.56);evidence.append({'quote':s.evidence,'source':'related skill'});status='PARTIAL';score=sim;reason='Related terminology appears in the resume, but the skill is not explicit.'
        if status in ('INDIRECT','PARTIAL') or conf<.6:
            question=f"Your resume provides {status.lower()} evidence for {r.skill or r.text}. Have you used this in a professional project? Please describe the work and duration."
        else:question=None
        found.append(EvidenceMatch(requirement_id=r.id,requirement=r.text,status=status,score=score,matched_evidence=evidence,bi_encoder_similarity=sim,cross_encoder_similarity=sim,graph_path=path,confidence=conf,reason=reason,question=question))
    return found
