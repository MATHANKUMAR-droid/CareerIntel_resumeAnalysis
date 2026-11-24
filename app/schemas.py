from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

class Candidate(BaseModel):
    name: str | None = None; email: str | None = None; phone: str | None = None; location: str | None = None; links: list[str] = []
class Skill(BaseModel):
    name: str; canonical_name: str; category: str = 'other'; years_experience: float | None = None
    proficiency: Literal['beginner','intermediate','advanced','expert'] | None = None
    source: Literal['explicit','inferred'] = 'explicit'; evidence: str; confidence: float = Field(ge=0,le=1); flags: list[str] = []
class Responsibility(BaseModel):
    text: str; skills_used: list[str] = []; evidence: str; confidence: float = Field(ge=0,le=1)
class Experience(BaseModel):
    title: str | None = None; company: str | None = None; start_date: str | None = None; end_date: str | None = None
    duration_months: int | None = None; is_leadership: bool = False; team_size: int | None = None
    responsibilities: list[Responsibility] = []; technologies: list[str] = []
class Education(BaseModel):
    degree: str; level: Literal['bachelor','master','phd','diploma','other'] = 'other'; field: str | None = None
    institution: str | None = None; start_year: int | None = None; end_year: int | None = None; grade: str | None = None
    evidence: str; confidence: float = Field(ge=0,le=1)
class Achievement(BaseModel):
    text: str; metric: str | None = None; impact_category: str = 'other'; related_role: str | None = None; evidence: str; confidence: float = Field(ge=0,le=1)
class Certification(BaseModel):
    name: str; issuer: str | None = None; year: int | None = None; evidence: str; confidence: float = Field(ge=0,le=1)
class Totals(BaseModel):
    total_experience_years: float = 0; leadership_years: float = 0; per_skill_years: dict[str,float] = {}
class Meta(BaseModel):
    source_file: str | None = None; extraction_method: str = 'nlp_only'; overall_confidence: float = .65; warnings: list[str] = []
class CandidateProfile(BaseModel):
    candidate: Candidate = Candidate(); summary: str = ''; skills: list[Skill] = []; experience: list[Experience] = []
    education: list[Education] = []; achievements: list[Achievement] = []; certifications: list[Certification] = []
    totals: Totals = Totals(); meta: Meta = Meta()
class Requirement(BaseModel):
    id: str; text: str; type: Literal['skill','experience_years','education','responsibility','soft'] = 'skill'
    mandatory: bool = True; min_years: float | None = None; skill: str | None = None; importance: int = Field(default=2,ge=1,le=3)
class JobProfile(BaseModel):
    title: str = 'Target role'; company: str | None = None; requirements: list[Requirement] = []; raw_text: str = ''
class EvidenceMatch(BaseModel):
    requirement_id: str; requirement: str; status: Literal['MET','PARTIAL','INDIRECT','MISSING']; score: float
    matched_evidence: list[dict] = []; bi_encoder_similarity: float = 0; cross_encoder_similarity: float = 0
    graph_path: list[str] = []; confidence: float = .6; reason: str; question: str | None = None
class Dimension(BaseModel):
    score: float; weight: float
class Clarification(BaseModel):
    id: str; requirement_id: str; question: str; answer: str | None = None; status: str = 'pending'
class JobFitAssessment(BaseModel):
    id: str; resume_id: str; job_id: str; overall_score: float; raw_score: float; classification: str
    mandatory_gaps: bool; dimensions: dict[str,Dimension]; requirements: list[EvidenceMatch]
    shap_contributions: dict[str,float] = {}; strengths: list[str] = []; gaps: list[str] = []; counterfactuals: list[str] = []
    clarifications: list[Clarification] = []; weights: dict[str,float] = {}; confidence_adjustment: float = 1
