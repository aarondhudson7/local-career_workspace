import subprocess
import time
import os
import sys
import httpx

OLLAMA_URL = "http://localhost:11434"

def is_ollama_running():
    """Check if Ollama server is currently listening on port 11434."""
    try:
        response = httpx.get(OLLAMA_URL, timeout=1.0)
        return response.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False

def start_ollama():
    """Launch Ollama cleanly as a headless background process."""
    if is_ollama_running():
        print("ℹ️ Ollama is already running.")
        return None
    
    print("🚀 Launching Ollama CLI background engine...")
    #  FIX: Launch the core engine directly instead of triggering the GUI helper app
    subprocess.Popen(
        ["ollama", "serve"], 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setpgrp # Detaches the process group so it doesn't swallow Ctrl+C prematurely
    )
    
    # Wait for the server to spin up and accept network connections
    attempts = 0
    while not is_ollama_running() and attempts < 15:
        time.sleep(1)
        attempts += 1
        print("⏳ Waiting for Ollama to become responsive...")
        
    if is_ollama_running():
        print("✅ Ollama is ready!")
    else:
        print("❌ Error: Ollama failed to start. Please check your system path.")
        sys.exit(1)

def stop_ollama():
    """Forcefully and reliably shut down all Ollama and local LLM server instances."""
    print("\n🛑 Terminating all local LLM processes...")
    
    # 1. Kill Ollama instances
    subprocess.run(["pkill", "-9", "ollama"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["killall", "-9", "Ollama"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 2.  FIX: Kill LM Studio / llama-server background instances
    subprocess.run(["pkill", "-9", "llama-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-9", "llama-ser"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 3. Final safety fallback using the port mapping ID directly if Ollama is still up
    if is_ollama_running():
        subprocess.run("kill -9 $(lsof -t -i:11434)", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    print("✅ Local LLM servers stopped successfully! Memory completely cleared.")


def run_streamlit():
    """Launch the Streamlit dashboard app and block execution until it is closed."""
    print("🖥️ Starting Streamlit workspace...")
    try:
        subprocess.run(["uv", "run", "streamlit", "run", "src/streamlit_app.py"])
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    # Ensure your script target exists
    if not os.path.exists("src/streamlit_app.py"):
         print("❌ Error: Please rename 'src/streamlit_app.py' inside this runner script to your actual Streamlit filename.")
         sys.exit(1)
         
    try:
        start_ollama()
        run_streamlit()
    finally:
        # Guarantees the kill routines run even if Streamlit crashes or exits via Ctrl+C
        stop_ollama()
