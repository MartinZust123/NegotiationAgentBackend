from openai import OpenAI
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_world_model(speaker, dialogue):
    prompt = f"""
    Generate a world model of {speaker} based on the following dialogue. 

    Dialogue: 
    {dialogue}

    That means you should analyze character traits, goals, beliefs, and emotional state of {speaker} based on the dialogue.

    Output should be a valid JSON object with the following structure:
    {{
        "CHARACTER": {{
            "Agreeableness": "very high/high/medium/low/very low",
            "Conscientiousness": "very high/high/medium/low/very low",
            "Neuroticism": "very high/high/medium/low/very low",
            "Openness to Experience": "very high/high/medium/low/very low",
            "Extraversion": "very high/high/medium/low/very low"
        }},
        "GOALS": ["goal1", "goal2", ...],
        "BELIEFS & KNOWLEDGE": ["belief1", "belief2", ...],
        "EMOTIONAL STATE": "one-word emotion"
    }}
    Ensure the response is a properly formatted JSON object.
    """

    print(prompt)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}  # Ensuring structured JSON output
    )

    # Parse the JSON response
    return json.loads(response.choices[0].message.content)

def give_advice(world_model, goals, conversation, speaker):
    system_prompt = """
    You are a professional negotiator. You are given a world model of another person, their goals, and a conversation between them and another person.
    You should analyze the world model and the conversation and give advice to the person on how to achieve their goals.
    Your advice MUST be extremely concise - no more than 50 words total.
    """
    
    prompt = f"""
    World model of another person:
    {world_model}

    Goals of person {speaker}:
    {goals}

    Conversation between the two people:
    {conversation}.

    Give advice to the {speaker} on how to achieve their goals. Your advice must be:
    1. Extremely concise (maximum 50 words)
    2. Precise and to the point
    3. Without any ** signs or formatting
    4. Actionable and specific
    """

    print("Sending prompt to OpenAI for advice generation...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
    )
    
    advice = response.choices[0].message.content
    word_count = len(advice.split())
    print(f"Received advice with {word_count} words")
    
    # If the response is still too long, truncate it
    if word_count > 50:
        print(f"Advice too long ({word_count} words). Truncating to 50 words...")
        words = advice.split()
        advice = ' '.join(words[:50])
        if not advice.endswith('.'):
            advice += '.'
    
    return advice