from dotenv import load_dotenv
import os

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "restaurant_reviews")

CSV_FILE = os.getenv(
    "CSV_FILE",
    "/home/tridao/Documents/rag/reviews_1mil.csv",
)

#qwen3-embedding:0.6b: Native 1024 dimensions, 32K context. 
#qwen3-embedding:4b: Native 2560 dimensions, 40K context. 
#qwen3-embedding:8b: Native 4096 dimensions, 40K context.

# embed_model = ["mxbai-embed-large", 1024]
# embed_model = ["qwen3-embedding", ]
# embed_model = ["nomic-embed-text", 768]
embed_model = ["qllama/bge-small-en-v1.5", 384]
# embed_model = ["all-minilm", 384]

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    embed_model[0],
)

EMBEDDING_DIM = os.getenv(
    "EMBEDDING_DIM",
    embed_model[1],
)
