from typing import List, Optional

from pydantic import BaseModel, Field


class Contacts(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None


class Education(BaseModel):
    degree: str
    institution: str
    year: Optional[str] = None


class WorkExperience(BaseModel):
    company: str
    title: str
    period: str
    description: str


class ResumeProfile(BaseModel):
    name: str
    contacts: Contacts
    years_experience: Optional[float] = None
    skills: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    work_history: List[WorkExperience] = Field(default_factory=list)


class ScoreResult(BaseModel):
    score: int
    matched_must_have: List[str] = Field(default_factory=list)
    missing_must_have: List[str] = Field(default_factory=list)
    matched_nice_to_have: List[str] = Field(default_factory=list)
    explanation: str


class Vacancy(BaseModel):
    title: str
    must_have_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    min_years_experience: float = 0
    description: str = ""
