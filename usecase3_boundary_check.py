import json
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load .env from same folder
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found")

client = OpenAI(api_key=api_key)


def read_input(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def boundary_check(input_text: str) -> bool:
    """
    Simple boundary rule example
    """
    forbidden_keywords = [
        "confidential",
        "personal data",
        "secret",
        "classified"
    ]

    text_lower = input_text.lower()

    for word in forbidden_keywords:
        if word in text_lower:
            return False

    return True


def ai_analysis(input_text: str) -> dict:

    prompt = f"""
You are a procurement risk analyst.

Evaluate the supplier and respond in JSON format.

Return format:
{{
"recommendation": "approve or reject",
"reason": "short explanation"
}}

Data:
{input_text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a procurement risk analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content
    return json.loads(content)


def create_cbp_node(ai_result: dict) -> dict:

    node = {
        "concept": "supplier approval",
        "intent": "reduce procurement risk",
        "boundary": "supplier must pass compliance check",
        "rationale": ai_result["reason"],
        "decision": ai_result["recommendation"],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    return node


def save_cbp_node(node: dict):

    path = os.path.join(base_dir, "cbp_node_boundary.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(node, f, indent=2, ensure_ascii=False)


def main():

    input_file = os.path.join(base_dir, "input_supplier.txt")

    input_text = read_input(input_file)

    print("Input:")
    print(input_text)
    print()

    allowed = boundary_check(input_text)

    if not allowed:
        print("BOUNDARY VIOLATION DETECTED")
        print("AI processing stopped.")
        return

    print("Boundary check passed.")
    print()

    ai_result = ai_analysis(input_text)

    print("AI analysis:")
    print(json.dumps(ai_result, indent=2, ensure_ascii=False))
    print()

    node = create_cbp_node(ai_result)

    save_cbp_node(node)

    print("CBP Node recorded.")


if __name__ == "__main__":
    main()