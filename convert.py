
import argparse, json
from pathlib import Path

try:
    from toon_format import encode, decode
except Exception as e:
    raise SystemExit("Please install toon-python: pip install git+https://github.com/toon-format/toon-python.git\nError: %s" % e)

def json_to_toon_file(json_path: Path) -> str:
    obj = json.loads(json_path.read_text(encoding='utf-8'))
    return encode(obj)

def toon_to_json_file(toon_path: Path) -> dict:
    toon_text = toon_path.read_text(encoding='utf-8')
    return decode(toon_text)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['to_toon', 'from_toon'])
    p.add_argument('file', help='input file path (json for to_toon, toon for from_toon)')
    args = p.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        raise SystemExit(f"File not found: {fp}")

    if args.action == 'to_toon':
        toon_data = json_to_toon_file(fp)
        output_path = fp.with_suffix('.toon') 
        output_path.write_text(toon_data, encoding='utf-8')
        print(f"Successfully converted and saved to {output_path}")
        print(json_to_toon_file(fp))
    else:
        obj = toon_to_json_file(fp)
        print(json.dumps(obj, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
