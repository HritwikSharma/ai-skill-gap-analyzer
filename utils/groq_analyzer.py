import json
from groq import Groq

def get_ai_analysis(profile, local_market_skills):
    # Highly recommended: Move this hardcoded string to st.secrets["groq"]["api_key"] later!
    client = Groq(api_key="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")
    
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
    
    # ─── UPDATED TO ACTIVE MODEL STRING ───
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-specdec",  # High-performance, low-latency 70B successor
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)
