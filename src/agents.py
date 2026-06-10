import time
import asyncio
from playwright.async_api import async_playwright
from langchain_core.documents import Document
from langchain_community.document_transformers import Html2TextTransformer
#from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq # shifting to Groq Cloud API
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import AsyncHtmlLoader, PyPDFLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_community.callbacks.manager import get_openai_callback

# PDF Compilation Imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# shifting to Groq Cloud API
import os
from dotenv import load_dotenv
load_dotenv()

class AgentOrchestrator:
    def __init__(self, model_name: str):
        self.model_name = model_name
        #self.llm = ChatOllama(model=model_name, temperature=0.5)
        self.llm = ChatGroq(model=model_name, temperature=0.5) # shifting to Groq Cloud API

    def extract_pdf_text(self, pdf_path: str):
        """Universal text extractor for resumes/documents."""
        start_time = time.time()
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        text = " ".join([page.page_content for page in pages])
        return text, time.time() - start_time

    def scrape_web_content(self, url: str):
      """Universal web scraping engine."""
      start_time = time.time()
      final_text = ""
      try:
        # Execute the async scrape function cleanly within Streamlit's event loop
        rendered_html = asyncio.run(scrape_dynamic_page(url))
            
        if rendered_html and len(rendered_html.strip()) > 500:
            # 1. Manually format the HTML string into a standard LangChain Document object
            raw_document = Document(
                    page_content=rendered_html,
                    metadata={"source": url, "title": "ICW Job Post"}
                )
                
            # 2. Use LangChain's markdown transformer to extract clean readable text blocks
            html2text = Html2TextTransformer()
            cleaned_docs = html2text.transform_documents([raw_document])
                                
            # 3. Pull the string text content out of the document item safely
            final_text = cleaned_docs[0].page_content
        else:
            print("The browser loaded, but returned empty content.")            
      except Exception as e:
        print(f"An error occurred during browser execution: {e}")
      
      return final_text, time.time() - start_time
    """ 
        # 1. Define a desktop browser header so the job site allows the request
        custom_headers = {
          "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
          "Accept-Language": "en-US,en;q=0.5",
        }
        loader = AsyncHtmlLoader(
            web_path=[url],
            header_template=custom_headers,
            trust_env=False # Prevents LangChain from routing requests through your Streamlit app's local port
        )
        docs = loader.load()
        bs_transformer = BeautifulSoupTransformer()
        docs_transformed = bs_transformer.transform_documents(
            docs, tags_to_extract=["p", "li", "div", "h1", "h2", "h3"]
        )
        text = " ".join([doc.page_content for doc in docs_transformed])[:4000]
    """

    def run_cover_letter_agent(self, resume_text: str, job_desc: str):
        """Agent #1: Cover Letter Specialist"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an elite career agent. Write a personalized, tailored cover letter. Clean formatting, no markdown symbols or placeholders. Max 500 words."),
            ("user", "JOB DESCRIPTION:\n{job_desc}\n\nRESUME:\n{resume}\n\nGenerate Cover Letter:")
        ])
        chain = prompt | self.llm
        
        start_time = time.time()
        with get_openai_callback() as cb:
            response = chain.invoke({"job_desc": job_desc, "resume": resume_text})
            metrics = {
                "duration": time.time() - start_time,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_tokens": cb.total_tokens
            }
        return response.content, metrics

    # --- FUTURE AGENTS HOOKS (Add your logic here later!) ---
    def run_resume_optimizer_agent(self, resume_text: str, job_desc: str):
        """Agent #2: Resume Tailoring & Gap Analysis Specialist"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an elite technical recruiter and resume strategist. Your task is to "
                "analyze the candidate's Resume against the Job Description. Produce a tailored "
                "version of their key experience sections and a clear gap analysis. "
                "Structure your response beautifully with plain text headings (e.g., GAP ANALYSIS, "
                "TAILORED BULLET POINTS). Avoid raw markdown symbols like ** or ### so the output "
                "renders beautifully in PDFs."
            )),
            ("user", (
                "JOB DESCRIPTION:\n{job_desc}\n\n"
                "CURRENT RESUME:\n{resume}\n\n"
                "Please rewrite relevant bullet points to match the target keywords and outline critical gaps:"
            ))
        ])
        chain = prompt | self.llm
        
        start_time = time.time()
        with get_openai_callback() as cb:
            response = chain.invoke({"job_desc": job_desc, "resume": resume_text})
            metrics = {
                "duration": time.time() - start_time,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_tokens": cb.total_tokens
            }
        return response.content, metrics

    def run_interview_prep_agent(self, resume_text: str, job_desc: str):
        """Agent #3: Behavioral and Technical Interview Prep Specialist"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert technical interviewer and leadership coach. Based on the "
                "provided Job Description and candidate Resume, generate a rigorous interview prep guide. "
                "Include: 3 specific technical questions based on the job requirements, 2 behavioral questions, "
                "and an ideal 'STAR' framework response strategy tailored to the candidate's actual background. "
                "Structure output cleanly with clear line breaks and headers. Do not use raw markdown asterisks."
            )),
            ("user", "JOB DESCRIPTION:\n{job_desc}\n\nRESUME:\n{resume}\n\nGenerate Custom Interview Guide:")
        ])
        chain = prompt | self.llm
        
        start_time = time.time()
        with get_openai_callback() as cb:
            response = chain.invoke({"job_desc": job_desc, "resume": resume_text})
            metrics = {
                "duration": time.time() - start_time,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_tokens": cb.total_tokens
            }
        return response.content, metrics

def compile_txt_to_pdf(text_content: str, output_path: str):
    """Utility to turn any raw text into a standard professional PDF."""
    start_time = time.time()
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
    )
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        'DocumentBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=11, leading=16, spaceAfter=12
    )
    story = []
    paragraphs = text_content.strip().split('\n')
    for para in paragraphs:
        clean_para = para.strip()
        if clean_para:
            clean_para = clean_para.replace("\n", "<br/>")
            story.append(Paragraph(clean_para, body_style))
    doc.build(story)
    return time.time() - start_time

# Custom function to handle dynamic JS loading using vanilla Playwright
async def scrape_dynamic_page(target_url: str) -> str:
    async with async_playwright() as p:
        # Launch a headless chromium instance
        browser = await p.chromium.launch(headless=True)
        # Emulate a desktop browser profile to avoid firewall triggers
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Navigate to the job portal and wait until network traffic calms down
        await page.goto(target_url, wait_until="networkidle", timeout=30000)
        
        # Grab the fully rendered inner HTML text
        html_content = await page.content()
        await browser.close()
        return html_content