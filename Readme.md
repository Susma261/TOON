# TOON 

This repo demonstrates TOON (Token-Oriented Object Notation) implementation and converting JSON to TOON and back, and benchmarking token counts for LLM prompt cost comparisons.

We use:
- `convert.py` — convert JSON → TOON and TOON → JSON (uses `toon_format.encode` / `decode`)
- `benchmark.py` — count tokens for JSON vs TOON (uses `toon_format.count_tokens` or `tiktoken` fallback)

**Result from our benchmark:**
--- TOON vs JSON token benchmark ---
Model: gpt-4o-mini
JSON length (chars): 4076
TOON length (chars): 859
JSON tokens: 1048
TOON tokens: 369
Reduction: 64.79%

## 📂 Project Structure

├── convert.py          
├── benchmark.py       
├── sample.json         
├── sample.toon         
├── requirements.txt   
└── README.md

## 🔧 Installation
git clone https://github.com/Susma261/TOON.git
cd <repo-name>

python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows

pip install -r requirements.txt

If toon_format is not installable through pip, install the official repo:
pip install git+https://github.com/toon-format/toon-python.git

## 📝 Sample Dataset
sample.json contains 30 employee records from a fictional company
sample.toon is a compact TOON representation

## 📬 Contact
LinkedIn: https://www.linkedin.com/in/susma-r/

