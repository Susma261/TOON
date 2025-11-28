#!/usr/bin/env python3
"""
llm_test.py — GROQ-only LLM test using TOON

Usage:
  - Put GROQ_API_KEY in .env (GROQ_MODEL optional)
  - python llm_test.py --file sample.json --question "Your question here"

Behavior:
 - Loads input JSON file (--file)
 - Encodes to TOON using toon_format.encode()
 - Sends TOON + question to Groq chat endpoint
 - Extracts TOON block from model reply
 - Decodes TOON -> JSON with toon_format.decode()
 - Prints raw reply, extracted TOON and parsed JSON
"""
import os
import re
import json
import argparse
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()  # load .env if present

from toon_format import encode, decode
import requests

# ----- configuration -----
GROQ_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_KEY:
    raise SystemExit("Please set GROQ_API_KEY in your environment or .env file.")

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

# ----- prompt builder -----
def build_prompt(toon_payload: str, instruction: str) -> str:
    return f"""You are a precise assistant.
The following data is provided in TOON format (do NOT add extra commentary):

{toon_payload}

Instruction:
{instruction}

Respond ONLY in TOON format. If you need to return a list, use a top-level key describing the result
(e.g., platform_employees:, top_salaries:). Use tabular shorthand if appropriate.
"""

# ----- robust TOON extractor -----
HEADER_RE = re.compile(r"(?m)^[ \t]*[A-Za-z0-9_\-]+(?:\[[0-9]+\])?(?:\{[^\}]*\})?\s*:\s*$")

def extract_toon_block(text: str) -> str:
    """Extract a TOON block from model reply. Return empty string if none found."""
    if not text or not text.strip():
        return ""

    text = text.replace("\r\n", "\n")
    m = HEADER_RE.search(text)
    if m:
        start = m.start()
        tail = text[start:]
        lines = tail.splitlines()
        out = []
        for ln in lines:
            # stop if we hit another top-level header after collecting some lines
            if out and re.match(r"^[A-Za-z0-9_\-]+\s*:", ln):
                break
            out.append(ln)
        result = "\n".join(out).strip()
        # If only header present, try to include the immediate following non-empty block
        if re.match(r"^[ \t]*[A-Za-z0-9_\-].*:\s*$", result) and len(result.splitlines()) == 1:
            following = tail.splitlines()[1:]
            extra = []
            for ln in following:
                if not ln.strip():
                    break
                extra.append(ln)
            if extra:
                result = result + "\n" + "\n".join(extra)
        return result

    # fallback: collect contiguous lines that look like TOON
    toon_lines = []
    for ln in text.splitlines():
        if re.match(r"^\s*(?:-|\w+(\[.*\])?(?:\{.*\})?:|\w+\s+\S+)", ln):
            toon_lines.append(ln)
        elif toon_lines:
            break
    return "\n".join(toon_lines).strip()

# ----- call GROQ chat endpoint -----
def call_groq_chat(prompt: str, model: str = GROQ_MODEL, max_tokens: int = 400, temperature: float = 0.0):
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    r = requests.post(GROQ_CHAT_URL, headers=headers, json=body, timeout=60)
    r.raise_for_status()
    resp = r.json()
    choice = resp.get("choices", [None])[0]
    if not choice:
        return ""
    msg = choice.get("message")
    if msg and isinstance(msg, dict):
        return msg.get("content") or ""
    return choice.get("text") or ""

# ----- main flow -----
def main():
    p = argparse.ArgumentParser(description="Send JSON (converted to TOON) to Groq and decode TOON reply.")
    p.add_argument("--file", "-f", required=True, help="Path to input JSON file")
    p.add_argument("--question", "-q", required=True, help="Instruction for the model (free text)")
    p.add_argument("--model", "-m", default=None, help="Override model id (optional)")
    p.add_argument("--max-tokens", type=int, default=400)
    p.add_argument("--temperature", type=float, default=0.0)
    args = p.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        raise SystemExit(f"File not found: {fp}")

    try:
        data = json.loads(fp.read_text(encoding="utf-8-sig"))
    except Exception as e:
        raise SystemExit(f"Failed to read/parse JSON: {e}")

    toon_payload = encode(data).strip()
    prompt = build_prompt(toon_payload, args.question)

    print("\n=== PROMPT (TOON preview) ===\n")
    print((toon_payload[:2000] + "...") if len(toon_payload) > 2000 else toon_payload)
    print("\n=== INSTRUCTION ===\n", args.question)
    print("\n=== SENDING TO GROQ ===\n")

    model = args.model if args.model else GROQ_MODEL

    try:
        reply = call_groq_chat(prompt, model=model, max_tokens=args.max_tokens, temperature=args.temperature)
    except Exception as e:
        raise SystemExit(f"Model call failed: {e}")

    print("\n=== RAW MODEL OUTPUT ===\n")
    print(reply)

    toon_block = extract_toon_block(reply)
    if not toon_block:
        print("\nNo TOON block extracted. Returning raw reply for inspection.")
        return

    print("\n=== EXTRACTED TOON BLOCK ===\n")
    print(toon_block)

    try:
        parsed = decode(toon_block)
        print("\n=== PARSED JSON ===\n")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except Exception as e:
        print("\nFailed to decode TOON:", e)
        print("\nRaw TOON block (for debugging):\n")
        print(toon_block)

if __name__ == "__main__":
    main()
