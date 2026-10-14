import os, sys, tempfile
tmp = tempfile.mkdtemp()
os.environ.update(DATABASE_URL=f"sqlite:///{tmp}/t.db", UPLOAD_DIR=f"{tmp}/up", QDRANT_PATH=f"{tmp}/q", OPENAI_API_KEY="test")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
