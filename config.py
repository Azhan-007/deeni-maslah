from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PDF_PATH = DATA_DIR / "Taleem-ul-Islam.pdf"
INDEX_DIR = BASE_DIR / "storage" / "faiss"
INDEX_FILE = INDEX_DIR / "index.faiss"
META_FILE = INDEX_DIR / "metadata.json"

# Models
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EN_TO_UR_MODEL = "Helsinki-NLP/opus-mt-en-ur"
UR_TO_EN_MODEL = "Helsinki-NLP/opus-mt-ur-en"
REWRITER_MODEL = "google/mt5-small"  # lightweight multilingual T5 for rewriting

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

# Retrieval
TOP_K = 5
SCORE_THRESHOLD = 0.30  # Cosine similarity threshold for a confident answer
CONFIDENCE_CLARIFY_THRESHOLD = 0.20  # If below, ask user to clarify

# API
CORS_ORIGINS = [
    "*"  # Adjust for production
]

# Misc
APP_NAME = "Deeni Q&A (Taleem-ul-Islam)"
DEFAULT_NOT_FOUND_UR = "اس کتاب میں اس کا واضح ذکر موجود نہیں۔"
DEFAULT_NOT_FOUND_EN = "This book does not mention this explicitly."
CLARIFY_UR = "براہِ کرم اپنا سوال واضح کریں۔"
CLARIFY_EN = "Please clarify your question."
