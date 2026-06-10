import subprocess
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_groq_key():
    """Verify the Groq API key is configured before launching."""
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY not found. Add it to your .env file.")
        sys.exit(1)
    print("✅ Groq API key found.")

def run_streamlit():
    """Launch the Streamlit dashboard app and block execution until it is closed."""
    print("🖥️ Starting Streamlit workspace...")
    try:
        subprocess.run(["uv", "run", "streamlit", "run", "src/streamlit_app.py"])
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    if not os.path.exists("src/streamlit_app.py"):
        print("❌ Error: Please rename 'src/streamlit_app.py' inside this runner script to your actual Streamlit filename.")
        sys.exit(1)

    check_groq_key()
    run_streamlit()
