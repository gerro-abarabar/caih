import json
import os
import re
from random import choice
from ollama import Client

def load_exam(file_path="assets"):
    # Ensure directory exists to avoid infinite loops
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    
    files = [f for f in os.listdir(file_path) if f.endswith(".json")]
    if not files:
        raise FileNotFoundError(f"No .json files found in {file_path}")
    
    file = choice(files)
    with open(os.path.join(file_path, file), "r", encoding="utf-8") as f:
        return json.load(f)

def get_exam_from_ai(questions):
    client = Client()
    exam_data = load_exam()
    
    # We only need a slice for context
    example_json = json.dumps(exam_data[0:questions-1], indent=2)

    messages = [
        {
            'role': 'system', 
            'content': (
                "You are a specialized JSON generator. Output ONLY a raw JSON array. "
                "No markdown blocks, no preamble, and no explanation. "
                "Ensure all newlines inside strings are escaped as '\\n'."
            )
        },
        {
            'role': 'user',
            'content': f"Create {questions} new questions following this schema: {example_json}. Use 0-3 for correct_answer index. Start the id from 1."
        },
    ]

    # Using Gemini 3 Flash for high reliability
    response = client.chat('gemini-3-flash-preview:latest', messages=messages, stream=False)
    raw_content = response.message.content 
    
    while True:
        try:
            # 1. Strip Markdown code blocks if the model included them
            clean_content = re.sub(r'```json|```', '', raw_content).strip()
            
            # 2. Extract the array using a non-greedy match to avoid "extra data" errors
            match = re.search(r'\[.*\]', clean_content, re.DOTALL)
            
            if match:
                json_str = match.group(0)
                
                # 3. Clean common invisible character culprits
                json_str = json_str.replace('\xa0', ' ')  # Non-breaking spaces
                json_str = json_str.replace('\t', ' ')    # Literal tabs
                
                return json.loads(json_str)
            else:
                raise ValueError("No JSON array found in the response.")
                
        except json.JSONDecodeError as e:
            print(f"CRITICAL: JSON Decode Failed at character {e.pos}")
            print(f"Context: {raw_content[max(0, e.pos-40):e.pos+40]}")
            print("redoing everything...")
            raise e

def explain_exam(exam):
    client = Client()
    messages = [
        {
            'role': 'user',
            'content': f'Provide a clear, educational explanation for these questions. Focus on the logic behind the correct answers: {json.dumps(exam)}',
        },
    ]
    # OSS is fine for prose/explanations
    response = client.chat('gpt-oss:120b-cloud', messages=messages, stream=False)
    return response.message.content.strip()

if __name__ == "__main__":
    # Test the AI generation
    try:
        new_exam = get_exam_from_ai()
        print(f"Successfully generated {len(new_exam)} questions.")
        print(json.dumps(new_exam[0], indent=2))
    except Exception as e:
        print(f"Error: {e}")