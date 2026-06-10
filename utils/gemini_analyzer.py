import json
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List

# 1. Structured Output Schema Definitions
class SkillItem(BaseModel):
    skill: str
    category: str
    priority_score: int
    difficulty_level: str

class RoadmapPhase(BaseModel):
    phase: int
    phase_name: str
    timeframe: str
    core_objective: str
    action_items: List[str]
    capstone_project: str
    estimated_hours_required: int

class CareerStrategySchema(BaseModel):
    skill_gap: List[str]
    structured_roadmap: List[RoadmapPhase]
    skill_inventory_matrix: List[SkillItem]

# 2. Execution Wrapper
def get_ai_analysis(profile, local_market_skills):
    # Initializes the client using your clean developer API key string
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    
    prompt = f"""
    You are an elite Engineering Career Strategist.
    Target Role: {profile.get('role', 'Developer')}
    Experience Tier: {profile.get('experience_level', 'Fresher')}
    Existing Skills: {', '.join(profile.get('skills', []))}
    Existing Tools/Infra: {', '.join(profile.get('tools_and_infra', []))}
    
    Our Database's Top Indian Market Demand Keywords: {local_market_skills}
    
    Provide a professional career strategy matching the CareerStrategySchema framework.
    """
    
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CareerStrategySchema,
            temperature=0.2
        ),
    )
    
    return json.loads(response.text)
