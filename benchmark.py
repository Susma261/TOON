import argparse
import json
from pathlib import Path

try:
    from toon_format import encode as to_toon, count_tokens as toon_count_tokens
except Exception:
    to_toon = None
    toon_count_tokens = None

if to_toon is None:
    try:
        from toon import to_toon  # older/other package name
    except Exception:
        to_toon = None

# tiktoken fallback for token counting
def tiktoken_count(text: str, model: str = "gpt-4o-mini") -> int:
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens for `text`. Prefer toon_format.count_tokens if available,
    otherwise use tiktoken.
    """
    if callable(toon_count_tokens):
        try:
            return toon_count_tokens(text)
        except Exception:
            pass
    return tiktoken_count(text, model)

def main():
    p = argparse.ArgumentParser(description="Compare token usage for JSON vs TOON")
    p.add_argument('--file', '-f', required=True, help='input JSON file')
    p.add_argument('--model', '-m', default='gpt-4o-mini', help='model name for token encoding')
    args = p.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        raise SystemExit(f'file not found: {fp}')

    json_text = fp.read_text(encoding='utf-8-sig')
    try:
        json_obj = json.loads(json_text)
    except Exception as e:
        raise SystemExit(f"Failed to parse JSON: {e}")

    if callable(to_toon):
        toon_text = to_toon(json_obj)
    else:
        def _simple_to_toon(obj, indent=0):
            pad = "\t" * indent
            lines = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        lines.append(f"{pad}{k}:")
                        lines.append(_simple_to_toon(v, indent + 1))
                    else:
                        lines.append(f"{pad}{k} {v}")
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        lines.append(f"{pad}-")
                        lines.append(_simple_to_toon(item, indent + 1))
                    else:
                        lines.append(f"{pad}- {item}")
            else:
                lines.append(f"{pad}{obj}")
            return "\n".join(lines)
        toon_text = _simple_to_toon(json_obj)

    jt = json_text.strip()
    tt = toon_text.strip()

    json_tokens = count_tokens(jt, args.model)
    toon_tokens = count_tokens(tt, args.model)

    reduction = (json_tokens - toon_tokens) / json_tokens * 100 if json_tokens else 0

    print('--- TOON vs JSON token benchmark ---')
    print('Model:', args.model)
    print('JSON length (chars):', len(jt))
    print('TOON length (chars):', len(tt))
    print('JSON tokens:', json_tokens)
    print('TOON tokens:', toon_tokens)
    print(f'Reduction: {reduction:.2f}%')

if __name__ == '__main__':
    main()
