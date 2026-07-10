"""
Web Search Module for ORDIS-A.I.
Provides web search capabilities using various search engines.
"""

import os
import sys
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urljoin
import time
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class WebSearch:
    def __init__(self, config: dict):
        """
        Initialize web search with configuration.

        Args:
            config: Configuration dictionary containing web search settings
        """
        self.config = config
        self.enabled = config.get('web_search', {}).get('enabled', True)
        self.provider = config.get('web_search', {}).get('provider', 'duckduckgo')
        self.safe_search = config.get('web_search', {}).get('safe_search', True)
        self.timeout = config.get('web_search', {}).get('timeout', 10)

        # Set up session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        if not self.enabled:
            logger.info("Web search is disabled in configuration")

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform a web search.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search result dictionaries
        """
        if not self.enabled:
            logger.warning("Web search is disabled")
            return []

        logger.info(f"Searching for: '{query}' using {self.provider}")

        try:
            if self.provider == 'duckduckgo':
                return self._search_duckduckgo(query, max_results)
            elif self.provider == 'google':
                return self._search_google(query, max_results)
            elif self.provider == 'bing':
                return self._search_bing(query, max_results)
            else:
                logger.warning(f"Unknown search provider: {self.provider}. Falling back to DuckDuckGo.")
                return self._search_duckduckgo(query, max_results)
        except Exception as e:
            logger.error(f"Error during web search: {e}")
            return []

    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search result dictionaries
        """
        try:
            # DuckDuckGo instant answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': quote_plus(query),
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }

            if self.safe_search:
                params['safe'] = 'on'
            else:
                params['safe'] = 'off'

            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            results = []

            # Add abstract if available
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', ''),
                    'snippet': data.get('Abstract', ''),
                    'url': data.get('AbstractURL', ''),
                    'source': 'DuckDuckGo Instant Answer'
                })

            # Add related topics
            for topic in data.get('RelatedTopics', []):
                if isinstance(topic, dict) and 'Text' in topic and 'FirstURL' in topic:
                    results.append({
                        'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', ''),
                        'snippet': topic.get('Text', ''),
                        'url': topic.get('FirstURL', ''),
                        'source': 'DuckDuckGo Related Topic'
                    })

            # Add results from related topics section
            for topic in data.get('RelatedTopics', []):
                if isinstance(topic, dict) and 'Topics' in topic:
                    for subtopic in topic['Topics']:
                        if isinstance(subtopic, dict) and 'Text' in subtopic and 'FirstURL' in subtopic:
                            results.append({
                                'title': subtopic.get('Text', '').split(' - ')[0] if ' - ' in subtopic.get('Text', '') else subtopic.get('Text', ''),
                                'snippet': subtopic.get('Text', ''),
                                'url': subtopic.get('FirstURL', ''),
                                'source': 'DuckDuckGo Related Topic'
                            })

            # If we need more results, try the HTML version
            if len(results) < max_results:
                html_results = self._search_duckduckgo_html(query, max_results - len(results))
                results.extend(html_results)

            # Limit results
            results = results[:max_results]

            logger.info(f"Found {len(results)} results from DuckDuckGo")
            return results

        except Exception as e:
            logger.error(f"Error searching DuckDuckGo: {e}")
            return []

    def _search_duckduckgo_html(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search DuckDuckGo using HTML scraping (fallback method).

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search result dictionaries
        """
        try:
            url = "https://duckduckgo.com/html/"
            params = {
                'q': quote_plus(query)
            }

            if self.safe_search:
                params['safe'] = 'on'
            else:
                params['safe'] = 'off'

            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            # Find result containers
            result_divs = soup.find_all('div', class_='result')
            for div in result_divs[:max_results]:
                try:
                    # Extract title
                    title_elem = div.find('a', class_='result__url')
                    title = title_elem.get_text(strip=True) if title_elem else ''

                    # Extract snippet/summary
                    snippet_elem = div.find('a', class_='result__snippet')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''

                    # Extract URL
                    link_elem = div.find('a', class_='result__url')
                    url = link_elem.get('href', '') if link_elem else ''

                    if title or snippet:
                        results.append({
                            'title': title,
                            'snippet': snippet,
                            'url': url,
                            'source': 'DuckDuckGo HTML'
                        })
                except Exception as e:
                    logger.debug(f"Error parsing result item: {e}")
                    continue

            return results

        except Exception as e:
            logger.error(f"Error in DuckDuckGo HTML search: {e}")
            return []

    def _search_google(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search using Google (requires custom search API or scraping).

        Note: This is a placeholder implementation. For production use,
        you would need to implement proper Google Custom Search API
        or use other search APIs.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search result dictionaries
        """
        logger.warning("Google search not fully implemented. Using DuckDuckGo as fallback.")
        return self._search_duckduckgo(query, max_results)

    def _search_bing(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search using Bing (requires API key or scraping).

        Note: This is a placeholder implementation. For production use,
        you would need to implement proper Bing Search API.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search result dictionaries
        """
        logger.warning("Bing search not fully implemented. Using DuckDuckGo as fallback.")
        return self._search_duckduckgo(query, max_results)

    def get_page_content(self, url: str, max_length: int = 5000) -> Optional[str]:
        """
        Fetch and extract text content from a web page.

        Args:
            url: URL to fetch
            max_length: Maximum length of content to return

        Returns:
            Extracted text content or None if error
        """
        if not self.enabled:
            logger.warning("Web search is disabled")
            return None

        try:
            logger.info(f"Fetching content from: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Parse HTML and extract text
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # Truncate if too long
            if len(text) > max_length:
                text = text[:max_length] + "... [truncated]"

            logger.info(f"Retrieved {len(text)} characters from {url}")
            return text

        except Exception as e:
            logger.error(f"Error fetching content from {url}: {e}")
            return None

    def search_and_summarize(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        """
        Search for information and provide a summary.

        Args:
            query: Search query string
            max_results: Maximum number of results to consider for summary

        Returns:
            Dictionary with search results and summary
        """
        results = self.search(query, max_results)

        if not results:
            return {
                'query': query,
                'results': [],
                'summary': "No results found.",
                'sources': []
            }

        # Extract snippets for summary
        snippets = [r.get('snippet', '') for r in results if r.get('snippet')]
        sources = [r.get('url', '') for r in results if r.get('url')]

        # Create a simple summary (in a real implementation, you might use NLP)
        summary = " ".join(snippets[:2])  # Just concatenate first two snippets for now
        if len(snippets) > 2:
            summary += " ..."

        return {
            'query': query,
            'results': results,
            'summary': summary.strip(),
            'sources': sources
        }

# Example usage
if __name__ == "__main__":
    # Configuration for testing
    config = {
        "web_search": {
            "enabled": True,
            "provider": "duckduckgo",
            "safe_search": True,
            "timeout": 10
        }
    }

    searcher = WebSearch(config)

    # Test search
    print("Testing web search...")
    results = searcher.search("Python programming language", max_results=3)

    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('title', 'No title')}")
        print(f"   URL: {result.get('url', 'No URL')}")
        print(f"   Snippet: {result.get('snippet', 'No snippet')[:100]}...")

    # Test search and summarize
    print("\n\nTesting search and summarize...")
    summary_result = searcher.search_and_summarize("Artificial intelligence", max_results=2)
    print(f"Query: {summary_result['query']}")
    print(f"Summary: {summary_result['summary']}")
    print(f"Sources: {summary_result['sources']}")