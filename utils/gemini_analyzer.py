import json
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List

# 1. Structured Output Schema Definitions
class SkillItem(BaseModel):
    skill: str
    category: str = Field(description="e.g., Core Language, Infrastructure, Data Layer, Frontend")
    priority_score: int = Field(description="Score from 1 to 10 evaluating job market demand priority")
    difficulty_level: str = Field(description="Must be exactly: Beginner, Intermediate, or Advanced")

class RoadmapPhase(BaseModel):
    phase: int
    phase_name: str
    timeframe: str = Field(description="e.g., Weeks 1-4")
    core_objective: str
    action_items: List[str]
    capstone_project: str = Field(description="A highly specific, production-ready portfolio project objective")
    estimated_hours_required: int

class CareerStrategySchema(BaseModel):
    skill_gap: List[str]
    structured_roadmap: List[RoadmapPhase]
    skill_inventory_matrix: List[SkillItem]

# 2. Execution Wrapper
def get_ai_analysis(profile, local_market_skills):
    # Initializes client utilizing your newly configured Streamlit App secrets matrix
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    
    prompt = f"""
    You are an elite Enterprise Tech Architect and Engineering Career Strategist.
    
    Target Profile:
    - Target Role: {profile.get('role', 'Data Analyst')}
    - Experience Tier: {profile.get('experience_level', 'Mid-Level')}
    - Existing Skills: {', '.join(profile.get('skills', []))}
    - Existing Tools/Infra: {', '.join(profile.get('tools_and_infra', []))}
    
    Our Local Database's Top Indian Market Demand Keywords for this exact role:
    {local_market_skills}
    
    TASK:
    Conduct a comprehensive technical gap analysis comparing the user's active tools against our market parameters.
    Provide an extensive engineering curriculum breaking down exactly what metrics they lack and map a structured phase progression.
    Ensure your response accurately fits the requested CareerStrategySchema format. Generate exactly 5 distinct structured roadmap phases.
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
