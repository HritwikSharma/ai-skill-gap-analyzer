import json
from groq import Groq

def get_ai_analysis(profile, local_market_skills):
    client = Groq(api_key="YOUR_GROQ_API_KEY")
    
    # We pass both: what we know (local) and the task to expand (global)
    prompt = f"""
    You are a Global Technical Market Researcher. 
    1. User Profile: {json.dumps(profile)}
    2. Our Database's Known Skills for this role: {local_market_skills}
    
    TASK:
    - Perform a comprehensive analysis of the target role '{profile['role']}'.
    - Compare our known skills against current, cutting-edge global market trends.
    - If a technology is trending globally but missing from our list, include it.
    - Return STRICT JSON with:
        "skill_gap": List of missing skills (include both local and globally emerging trends).
        "comprehensive_roadmap": [List of 7 detailed actionable steps].
        "skill_inventory": {{"skill_name": "difficulty_level"}}.
    """
    
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)
