# TOON 

This repo demonstrates TOON (Token-Oriented Object Notation) implementation and converting JSON to TOON and back, and benchmarking token counts for LLM prompt cost comparisons.

We use:
- `convert.py` — convert JSON → TOON and TOON → JSON (uses `toon_format.encode` / `decode`)
- `benchmark.py` — count tokens for JSON vs TOON (uses `toon_format.count_tokens` or `tiktoken` fallback)

**Result from our benchmark:**<br>
--- TOON vs JSON token benchmark ---<br>
Model: gpt-4o-mini<br>
JSON length (chars): 4076<br>
TOON length (chars): 859<br>
JSON tokens: 1048<br>
TOON tokens: 369<br>
Reduction: 64.79%<br>


## 📂 Project Structure

├── convert.py          
├── benchmark.py       
├── sample.json         
├── sample.toon         
├── requirements.txt   
└── README.md

## 🔧 Installation:

git clone https://github.com/Susma261/TOON.git <br>
cd TOON

- `python -m venv venv`
- `source venv/bin/activate`
- `venv\Scripts\activate`         

- `pip install -r requirements.txt`

*If toon_format is not installable through pip, install the official repo:*<br>
- `https://github.com/toon-format/toon-python.git`

## 📝 Sample Dataset:

- `sample.json` contains 30 employee records from a fictional company<br>
- `sample.toon` is a compact TOON representation

## 📬 Contact:
LinkedIn: https://www.linkedin.com/in/susma-r/









