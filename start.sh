#!/bin/bash

echo "🧹 Wiping existing ChromaDB..."
rm -rf chroma_db

echo "⚡ Running ingest.py to rebuild ChromaDB..."
python ingest.py

echo "🚀 Launching backend..."
uvicorn backend:app --host 0.0.0.0 --port 8000
