import os
import signal
import time  # Added to track performance duration for cache hits
import streamlit as st
from src.agents import AgentOrchestrator, compile_txt_to_pdf
from src.cache import get_cached_job, save_job_to_cache  # Import cache tools

# --- DASHBOARD PLATFORM LAYOUT ---
st.set_page_config(page_title="Multi-Agent Workspace", layout="wide", page_icon="🏢")
st.title("🏢 Local Multi-Agent Workspace & Executive Hub")
st.write("Offline analytics engineered directly for Apple Silicon M4 Core Architecture.")

# Initialize app session memory keys
if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "metrics" not in st.session_state:
    st.session_state.metrics = {}
if "step_logs" not in st.session_state:
    st.session_state.step_logs = []

# --- SIDEBAR ORCHESTRATION ---
st.sidebar.header("🕹️ Control Panel")
agent_selection = st.sidebar.selectbox(
    "Active AI Specialist", 
    ["Cover Letter Agent", "Resume Tailor Agent", "Interview Coach"]
)

model_choice = st.sidebar.selectbox("Local Compute Engine", ["llama3", "mistral", "gemma2"])
job_url = st.sidebar.text_input("Job Profile Link Target", "https://ycombinator.com")

# Cache expiration interval slider selector
cache_expiry_days = st.sidebar.slider("Cache Expiry Refresh Interval (Days)", min_value=1, max_value=30, value=7)

uploaded_file = st.sidebar.file_uploader("Supply Workspace Context (PDF Resume)", type=["pdf"])

# Run processing chain
if st.sidebar.button("⚡ Run Agent Pipeline", disabled=(uploaded_file is None)):
    st.session_state.step_logs = []
    st.session_state.generated_text = ""
    
    orchestrator = AgentOrchestrator(model_name=model_choice)
    temp_resume_path = "temp_resume.pdf"
    
    with open(temp_resume_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # Step 1: Document Digestion
        with st.spinner("Processing Context Document..."):
            resume_text, t1 = orchestrator.extract_pdf_text(temp_resume_path)
            st.session_state.step_logs.append(f"✔️ Step 1: Extracted source PDF data successfully ({t1:.2f}s)")

        # Step 2: Target Data Gathering (WITH SMART REFRESH CACHE)
        with st.spinner("Checking cache and harvesting URL requirements..."):
            start_time = time.time()
            
            # Look for locally saved data profile mapping matching target parameters
            cached_text = get_cached_job(job_url, max_days=cache_expiry_days)
            
            if cached_text:
                job_desc = cached_text
                t2 = time.time() - start_time
                st.session_state.step_logs.append(f"📦 Step 2: Loaded job data profile locally from cache database ({t2:.4f}s)")
            else:
                # Cache missed or expired: Execute a direct Playwright web scrape sequence
                job_desc, t2 = orchestrator.scrape_web_content(job_url)
                save_job_to_cache(job_url, job_desc)
                st.session_state.step_logs.append(f"🌐 Step 2: Cache miss. Scraped online target page and saved locally ({t2:.2f}s)")

        # Step 3: Core Specialized Intelligence Task Route
        if agent_selection == "Cover Letter Agent":
            with st.spinner("Executing Cover Letter Specialist Task..."):
                output, metrics = orchestrator.run_cover_letter_agent(resume_text, job_desc)
                st.session_state.generated_text = output
                st.session_state.metrics = metrics
                st.session_state.step_logs.append(f"✔️ Step 3: Cover Letter generated ({metrics['duration']:.2f}s)")
                
        elif agent_selection == "Resume Tailor Agent":
            with st.spinner("Executing Resume Tailoring Specialist Task..."):
                output, metrics = orchestrator.run_resume_optimizer_agent(resume_text, job_desc)
                st.session_state.generated_text = output
                st.session_state.metrics = metrics
                st.session_state.step_logs.append(f"✔️ Step 3: Resume modifications generated ({metrics['duration']:.2f}s)")

        elif agent_selection == "Interview Coach":
            with st.spinner("Executing Interview Preparation Specialist Task..."):
                output, metrics = orchestrator.run_interview_prep_agent(resume_text, job_desc)
                st.session_state.generated_text = output
                st.session_state.metrics = metrics
                st.session_state.step_logs.append(f"✔️ Step 3: Interview prep materials generated ({metrics['duration']:.2f}s)")

    finally:
        if os.path.exists(temp_resume_path):
            os.remove(temp_resume_path)

# Graceful Shutdown Button
st.sidebar.markdown("---")
if st.sidebar.button("🛑 Shut Down Workspace", use_container_width=True):
    st.sidebar.success("Shutting down... You can close this browser tab.")
    os.kill(os.getpid(), signal.SIGINT)

# --- CENTRAL WORKSPACE DISPLAY ---
log_col, main_col = st.columns([0.3, 0.7])

with log_col:
    st.subheader("📋 Execution Tracker")
    if st.session_state.step_logs:
        for log in st.session_state.step_logs:
            st.info(log)
    else:
        st.caption("Awaiting environment execution commands...")

with main_col:
    st.subheader("🛠️ Workspace Output Canvas")
    
    if st.session_state.generated_text:
        edited_text = st.text_area(
            label="Modify or fine-tune your agent's text output directly inside this canvas:",
            value=st.session_state.generated_text,
            height=350
        )
        
        st.markdown("### 📊 Local Resource Audit")
        m = st.session_state.metrics
        c1, c2, c3 = st.columns(3)
        c1.metric(label="Inbound Input Tokens", value=m.get("prompt_tokens") or "N/A")
        c2.metric(label="Outbound Tokens Compiled", value=m.get("completion_tokens") or "N/A")
        c3.metric(label="Financial Overhead", value="$0.00", delta="Apple Metal Hardware")

        output_pdf_path = "workspace_final_document.pdf"
        if st.button("💾 Compile & Render Final Document PDF"):
            with st.spinner("Baking finalized typography into standard PDF..."):
                t4 = compile_txt_to_pdf(edited_text, output_pdf_path)
                st.success(f"✨ Document compiled cleanly locally in {t4:.2f}s!")
                
            with open(output_pdf_path, "rb") as file:
                st.download_button(
                    label="📥 Save Final Document To Mac Finder (.pdf)",
                    data=file,
                    file_name="Final_Document.pdf",
                    mime="application/pdf"
                )
    else:
        st.info("Configure your parameters in the left side control deck to generate your text workspace canvas.")

import sqlite3
import pandas as pd

# --- OPTIMIZED CACHE DATABASE INSPECTOR ---
st.markdown("---")

# Wrap the inspector inside an expander so it stays collapsed by default
with st.expander("🗄️ Inspect Local Cache Database", expanded=False):
    try:
        # The code inside this block only runs if the user clicks to expand it
        with sqlite3.connect("job_cache.db") as conn:
            df = pd.read_sql_query("SELECT url, cached_at, url_hash FROM job_listings", conn)
        
        if not df.empty:
            st.write(f"Total Cached Jobs: `{len(df)}`")
            # Render the data frame
            st.dataframe(df, use_container_width=True)
            
            # Action button to wipe data cleanly
            if st.button("🗑️ Clear Entire Cache Database", type="secondary", use_container_width=True):
                with sqlite3.connect("job_cache.db") as conn:
                    conn.execute("DELETE FROM job_listings")
                st.success("Cache database cleared completely!")
                st.rerun()
        else:
            st.info("The cache database is initialized but currently empty.")
            
    except Exception as e:
        st.caption("Cache database file not initialized yet. Execute a pipeline task to create it.")
