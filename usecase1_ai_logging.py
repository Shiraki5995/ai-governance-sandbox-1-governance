import json
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def read_input_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


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


def save_cbp_node(node: dict, file_path: str = "cbp_node.json") -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(node, f, indent=2, ensure_ascii=False)


def main() -> None:
    input_text = read_input_file("input_supplier.txt")

    print("Input data:")
    print(input_text)
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
    
    