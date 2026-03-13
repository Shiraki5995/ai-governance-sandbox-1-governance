import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env in the same folder as this script
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY was not found in .env")

client = OpenAI(api_key=api_key)


def read_cbp_node(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def replay_decision(node: dict) -> str:
    prompt = f"""
You are an organizational decision review assistant.

A past decision was recorded in a structured node.

Please explain clearly:
1. what decision was made
2. why it was made
3. what boundary condition was applied
4. what future monitoring or caution may be appropriate

Recorded node:
{json.dumps(node, indent=2, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "You explain past organizational decisions based on structured records."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


def main() -> None:
    node_file = os.path.join(base_dir, "cbp_node.json")
    node = read_cbp_node(node_file)

    print("Recorded CBP Node:")
    print(json.dumps(node, indent=2, ensure_ascii=False))
    print()

    replay_text = replay_decision(node)

    print("Decision Replay:")
    print(replay_text)
    print()


if __name__ == "__main__":
    main()
    
    