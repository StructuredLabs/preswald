import asyncio
import os
from socket import timeout

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests


async def export_to_html(url:str,output_path:str):
    """Export a Preswald app to a static HTML page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
        )
        page = await browser.new_page(viewport={"width": 1920, "height": 1080}) # Set a reasonable viewport size
        await page.goto(url)
        await page.wait_for_selector(".dashboard-container",timeout=50000)
        curr_height=0
        max=await page.evaluate("document.body.scrollHeight")
        while True:
            if curr_height >= max:
                break
            curr_height+=500
            await page.evaluate(f"window.scrollTo(0, {curr_height})")
            await page.wait_for_timeout(1000)  # Allow time for lazy loading

        html_content = await page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        for link_tag in soup.find_all("link",rel='stylesheet'):
            css_url = link_tag['href']
            if not css_url.startswith(('http://', 'https://')):
                base_url = url if not url.endswith('/') else url[:-1]
                css_url = f'{base_url}{css_url}'

            try:
                response = requests.get(css_url,stream=True)
                response.raise_for_status()
                response.encoding='utf-8'
                style_tag=soup.new_tag("style")
                style_tag.string=response.text
                link_tag.replace_with(style_tag)
            except requests.exceptions.RequestException as e:
                print(f"Warning: Could not fetch CSS from {css_url}. Error: {e}")
                continue

        final_html_content=soup.prettify()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html_content)
        await browser.close()


async def export_to_pdf(url: str, output_path: str):
    """Export a Preswald app to a PDF file."""
    async with async_playwright() as p:
        browser = await p.chromium.launch() 
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.goto(url)
        await page.wait_for_selector(".dashboard-container",timeout=50000)
        
        curr_height=0
        max=await page.evaluate("document.body.scrollHeight")
        while True: 
            if curr_height >= max:
                break
            curr_height+=500
            await page.evaluate(f"window.scrollTo(0, {curr_height})")
            await page.wait_for_timeout(1000)  # Allow time for lazy loading
        os.makedirs(os.path.dirname(output_path), exist_ok=True) # Ensure directory exists
        await page.pdf(path=output_path) # Use Playwright's pdf method
        await browser.close()

 
def export_html_sync(url:str,output_path:str):
    asyncio.run(export_to_html(url,output_path))


def export_pdf_sync(url:str,output_path:str):
    asyncio.run(export_to_pdf(url,output_path))

if __name__ == "main":
    app_url="http://localhost:8501"
    output_path="./report.html"
    export_html_sync(app_url, output_path)
    print(f"App exported to {output_path}")