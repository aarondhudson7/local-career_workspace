url = "https://careers.icwgroup.com/san-diego-ca/senior-applied-ai-engineer/C50236D81FA54F1F8B6B353A530BBF32/job/"
import streamlit as st
import asyncio
from playwright.async_api import async_playwright
from langchain_core.documents import Document
from langchain_community.document_transformers import Html2TextTransformer

st.title("Dynamic Job Scraper App")

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

if st.button("Scrape Job Details"):
    try:
        with st.spinner("Launching native Playwright engine to process JavaScript..."):
            # Execute the async scrape function cleanly within Streamlit's event loop
            rendered_html = asyncio.run(scrape_dynamic_page(url))
            
        if rendered_html and len(rendered_html.strip()) > 500:
            with st.spinner("Cleaning rendered layout using BeautifulSoup/Html2Text..."):
                # 1. Manually format the HTML string into a standard LangChain Document object
                raw_document = Document(
                    page_content=rendered_html,
                    metadata={"source": url, "title": "ICW Job Post"}
                )
                
                # 2. Use LangChain's markdown transformer to extract clean readable text blocks
                html2text = Html2TextTransformer()
                cleaned_docs = html2text.transform_documents([raw_document])
                
                st.success("Successfully captured dynamically rendered text!")
                
                # 3. Pull the string text content out of the document item safely
                final_text = cleaned_docs[0].page_content
                st.text_area("Scraped Content Preview", final_text[:2000], height=400)
        else:
            st.error("The browser loaded, but returned empty content.")
            
    except Exception as e:
        st.error(f"An error occurred during browser execution: {e}")

