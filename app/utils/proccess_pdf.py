import json
import tempfile
import logging
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text
from transformers import pipeline as hf_pipeline, AutoTokenizer, AutoModelForTokenClassification

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def map_label(label: str) -> str:
    if label == "O":
        return label
    return label.split("-")[-1]

def merge_tokens(tokens):
    merged = []
    if not tokens:
        return merged
    current = tokens[0].copy()
    for token in tokens[1:]:
        if token["entity"] == current["entity"] and token["start"] == current["end"]:
            current["word"] += token["word"]
            current["end"] = token["end"]
        else:
            merged.append(current)
            current = token.copy()
    merged.append(current)
    return merged

def remove_special_characters(word: str) -> str:
    if word and word[0] == "▁":
        word = word[1:]
    return word.replace("▁", " ")

MAX_TOKENS = 512
def chunk_text(text, tokenizer, max_tokens=MAX_TOKENS):
    tokens = tokenizer.encode(text, add_special_tokens=False)
    for i in range(0, len(tokens), max_tokens):
        chunk = tokens[i:i + max_tokens]
        yield tokenizer.decode(chunk, skip_special_tokens=True)

MODEL_NAME = "iiiorg/piiranha-v1-detect-personal-information"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)
nlp = hf_pipeline("token-classification", model=model, tokenizer=tokenizer, device=-1)

def extract_pii(pdf_path: str) -> list[dict]:
    text = extract_text(pdf_path)
    results = []
    for chunk in chunk_text(text, tokenizer):
        chunk_results = nlp(chunk)
        results.extend(chunk_results)

    results = merge_tokens(results)
    for r in results:
        r["entity"] = map_label(r["entity"])
        r["word"] = remove_special_characters(r["word"])

    return [
        {
            "entity": r.get("entity_group", r.get("entity")),
            "score": float(r["score"]),
            "word": r["word"],
            "start": r.get("start"),
            "end": r.get("end"),
        }
        for r in results
    ]

def redact(pdf_path: str, pii_list: list[str]) -> str:
    """Redact by searching for each PII word string and applying black boxes. Returns temp PDF path."""
    doc = fitz.open(pdf_path)
    for page in doc:
        for word in pii_list:
            if not word:
                continue
            for inst in page.search_for(word):
                page.add_redact_annot(inst, fill=(0, 0, 0))
        page.apply_redactions()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_path = tmp.name
    tmp.close()
    doc.save(tmp_path)
    doc.close()
    return tmp_path
