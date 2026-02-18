"""
Zemi Browser Module
Handles web searches using Brave Search API
"""

import asyncio
import requests
import json
from datetime import datetime
from cryptography.fernet import Fernet
from pathlib import Path

class BrowserController:
    def __init__(self):
        self.api_key = self._load_brave_key()
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        print("🌐 Browser controller initialized")
    
    def _load_brave_key(self):
        """Load Brave API key from encrypted vault"""
        try:
            vault_dir = Path("/Users/zemi/ZemiV1/vault")
            
            with open(vault_dir / "master.key", 'rb') as key_file:
                key = key_file.read()
            
            fernet = Fernet(key)
            
            with open(vault_dir / "brave_search.enc", 'rb') as enc_file:
                encrypted = enc_file.read()
            
            api_key = fernet.decrypt(encrypted).decode()
            print("🔑 Brave API key loaded")
            return api_key
            
        except Exception as e:
            print(f"❌ Failed to load Brave API key: {e}")
            return None
    
    async def search_web(self, query, num_results=3):
        """
        Perform web search using Brave Search API
        Returns structured results
        """
        
        if not self.api_key:
            return "❌ Brave API key not configured"
        
        print(f"🔍 Searching for: {query}")
        
        try:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": num_results,
                "search_lang": "en",
                "safesearch": "moderate"
            }
            
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._format_results(query, data)
            else:
                return f"❌ Search failed: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ Search error: {str(e)}"
    
    def _format_results(self, query, data):
        """Format search results for display"""
        
        results = data.get('web', {}).get('results', [])
        
        if not results:
            return f"No results found for: {query}"
        
        response = f"🔍 **Brave Search Results for:** {query}\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('description', 'No description')
            url = result.get('url', '')
            
            response += f"**{i}. {title}**\n"
            response += f"{snippet}\n"
            response += f"🔗 {url}\n\n"
        
        response += f"_Searched at {datetime.now().strftime('%I:%M %p')}_"
        
        return response
    
    async def fetch_page_content(self, url):
        """Fetch content from a specific URL"""
        
        print(f"📄 Fetching: {url}")
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Simple text extraction
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove scripts and styles
                for tag in soup(['script', 'style', 'nav', 'footer']):
                    tag.decompose()
                
                text = soup.get_text(separator='\n', strip=True)
                return text[:2000]
            else:
                return f"❌ Failed to fetch: {response.status_code}"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"

# Test
if __name__ == "__main__":
    async def test():
        browser = BrowserController()
        results = await browser.search_web("Python tutorials", 3)
        print(results)
    
    asyncio.run(test())

