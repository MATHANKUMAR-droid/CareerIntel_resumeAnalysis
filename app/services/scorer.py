from app.schemas import *
DEFAULT={'skills':.35,'experience':.25,'education':.10,'responsibilities':.15,'achievements':.15}
def score_assessment(profile,job,matches,weights=None,assessment_id=''):
    w=weights or DEFAULT.copy(); total=sum(w.values()) or 1;w={k:v/total for k,v in w.items()}
    skill=[(m.score,next((r.importance for r in job.requirements if r.id==m.requirement_id),2)) for m in matches if next((r.type for r in job.requirements if r.id==m.requirement_id),'')=='skill']
    dims={}
    dims['skills']=sum(s*i for s,i in skill)/sum(i for _,i in skill)*100 if skill else 0
    yrs=[r.min_years for r in job.requirements if r.type=='skill' and r.min_years]
    dims['experience']=min(100,profile.totals.total_experience_years/max(yrs or [1])*100)
    dims['education']=100 if any(e.level in ('master','phd') for e in profile.education) else 55 if profile.education else 25
    resp=[m.score for m in matches if next((r.type for r in job.requirements if r.id==m.requirement_id),'')=='responsibility']
    dims['responsibilities']=(sum(resp)/len(resp)*100) if resp else 65
    dims['achievements']=min(100,55+len(profile.achievements)*8)
    raw=sum(w[k]*dims[k] for k in w); conf=sum(m.confidence for m in matches)/len(matches) if matches else .5
    adjustment=.9+.1*conf; adjusted=raw*adjustment
    label='Excellent Match' if adjusted>=85 else 'Strong Match' if adjusted>=70 else 'Moderate Match' if adjusted>=55 else 'Weak Match' if adjusted>=40 else 'Poor Match'
    mandatory_gaps=any(m.status=='MISSING' and next((r.mandatory for r in job.requirements if r.id==m.requirement_id),False) for m in matches)
    clar=[]
    for m in matches:
        if m.question:clar.append(Clarification(id='Q'+m.requirement_id,requirement_id=m.requirement_id,question=m.question))
    strengths=[f"{m.requirement}: {m.status.lower()} ({m.score:.0%})" for m in matches if m.status=='MET'][:5]
    gaps=[f"{m.requirement}: {m.status.lower()}" for m in matches if m.status!='MET'][:5]
    # Exact Shapley contribution for additive weighted dimensions with neutral 50 baseline.
    shap={k:round(w[k]*(dims[k]-50),2) for k in w}
    counter=[f"If you verify {m.requirement}, the score can improve when the requirement is re-evaluated." for m in matches if m.status in ('INDIRECT','PARTIAL','MISSING')][:3]
    return JobFitAssessment(id=assessment_id,resume_id='',job_id='',overall_score=round(adjusted,1),raw_score=round(raw,1),classification=label,mandatory_gaps=mandatory_gaps,dimensions={k:Dimension(score=round(dims[k],1),weight=round(w[k],3)) for k in w},requirements=matches,shap_contributions=shap,strengths=strengths,gaps=gaps,counterfactuals=counter,clarifications=clar,weights=w,confidence_adjustment=round(adjustment,3))
