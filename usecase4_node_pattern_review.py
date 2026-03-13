import json
import os
from glob import glob
from dotenv import load_dotenv
from openai import OpenAI

# Base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Load .env
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key)


def load_nodes(nodes_dir: str) -> list:
    file_paths = glob(os.path.join(nodes_dir, "*.json"))
    nodes = []

    for path in file_paths:
        with open(path, "r", encoding="utf-8") as f:
            nodes.append(json.load(f))

    return nodes


def review_patterns(nodes: list) -> str:
    prompt = f"""
You are an organizational decision pattern analyst.

Below are multiple recorded CBP Nodes representing past supplier approval decisions.

Please analyze them and explain clearly:

1. What recurring decision patterns can be observed
2. What boundary conditions appear repeatedly
3. What organizational risk posture seems to emerge
4. What this suggests about the organization's decision style

Recorded nodes:
{json.dumps(nodes, indent=2, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "You analyze organizational decision patterns from structured decision records."
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
    nodes_dir = os.path.join(base_dir, "nodes")
    nodes = load_nodes(nodes_dir)

    print("Loaded nodes:")
    print(json.dumps(nodes, indent=2, ensure_ascii=False))
    print()

    analysis = review_patterns(nodes)

    print("Pattern Review:")
    print(analysis)
    print()


if __name__ == "__main__":
    main()