#!/usr/bin/env python3
"""
MediaWiki Scraper for AnythingLLM
Exports all pages from a MediaWiki instance to text files.
"""

import os
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime

try:
    import mwclient
except ImportError:
    print("Error: mwclient is required. Install with: pip install mwclient")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables only.")
    load_dotenv = None


def sanitize_filename(title: str) -> str:
    """Convert wiki page title to a safe filename."""
    # Replace problematic characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', title)
    safe_name = re.sub(r'\s+', '_', safe_name)
    safe_name = safe_name.strip('._')
    # Limit length
    if len(safe_name) > 200:
        safe_name = safe_name[:200]
    return safe_name


def get_page_content(page) -> str:
    """Extract content from a MediaWiki page."""
    try:
        # Get the raw wikitext content
        text = page.text()
        
        # Create a formatted document
        content = f"""# {page.name}

{text}

---
Source: MediaWiki
Page: {page.name}
Last Modified: {page.touched if hasattr(page, 'touched') else 'Unknown'}
"""
        return content
    except Exception as e:
        print(f"  Warning: Could not get content for '{page.name}': {e}")
        return None


def scrape_mediawiki(
    wiki_url: str,
    wiki_path: str = "/",
    output_dir: str = "./wiki_export",
    username: str = None,
    password: str = None,
    namespace: int = 0,  # 0 = Main namespace
    limit: int = None
):
    """
    Scrape all pages from a MediaWiki instance.
    
    Args:
        wiki_url: MediaWiki server URL (e.g., 'wiki.royaltek.com')
        wiki_path: Path to wiki API (usually '/' or '/w/')
        output_dir: Directory to save exported pages
        username: Optional username for authentication
        password: Optional password for authentication
        namespace: MediaWiki namespace to scrape (0 = main articles)
        limit: Maximum number of pages to scrape (None = all)
    """
    print(f"Connecting to MediaWiki at {wiki_url}...")
    
    # Determine scheme
    scheme = 'https'
    if wiki_url.startswith('http://'):
        scheme = 'http'
        wiki_url = wiki_url.replace('http://', '')
    elif wiki_url.startswith('https://'):
        wiki_url = wiki_url.replace('https://', '')
    
    try:
        site = mwclient.Site(wiki_url, path=wiki_path, scheme=scheme)
        print(f"Connected successfully to {wiki_url}")
    except Exception as e:
        print(f"Error connecting to MediaWiki: {e}")
        sys.exit(1)
    
    # Login if credentials provided
    if username and password:
        try:
            site.login(username, password)
            print(f"Logged in as {username}")
        except Exception as e:
            print(f"Warning: Login failed: {e}")
            print("Continuing without authentication...")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_path.absolute()}")
    
    # Get all pages
    print(f"\nFetching pages from namespace {namespace}...")
    pages = site.allpages(namespace=namespace)
    
    exported_count = 0
    error_count = 0
    
    for i, page in enumerate(pages):
        if limit and i >= limit:
            print(f"\nReached limit of {limit} pages.")
            break
        
        try:
            title = page.name
            print(f"[{i+1}] Exporting: {title}")
            
            # Get page content
            content = get_page_content(page)
            if content is None:
                error_count += 1
                continue
            
            # Save to file
            filename = sanitize_filename(title) + ".txt"
            filepath = output_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            exported_count += 1
            
        except Exception as e:
            print(f"  Error processing page: {e}")
            error_count += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Export Complete!")
    print(f"  - Pages exported: {exported_count}")
    print(f"  - Errors: {error_count}")
    print(f"  - Output directory: {output_path.absolute()}")
    print(f"{'='*50}")
    
    return exported_count


def main():
    parser = argparse.ArgumentParser(
        description='Export MediaWiki pages to text files for AnythingLLM import'
    )
    parser.add_argument(
        '--url', '-u',
        default=os.getenv('MEDIAWIKI_URL'),
        help='MediaWiki URL (e.g., wiki.example.com)'
    )
    parser.add_argument(
        '--path', '-p',
        default=os.getenv('MEDIAWIKI_PATH', '/'),
        help='Wiki path (default: /)'
    )
    parser.add_argument(
        '--output', '-o',
        default='./wiki_export',
        help='Output directory (default: ./wiki_export)'
    )
    parser.add_argument(
        '--username',
        default=os.getenv('MEDIAWIKI_USERNAME'),
        help='MediaWiki username for authentication'
    )
    parser.add_argument(
        '--password',
        default=os.getenv('MEDIAWIKI_PASSWORD'),
        help='MediaWiki password for authentication'
    )
    parser.add_argument(
        '--namespace', '-n',
        type=int,
        default=0,
        help='MediaWiki namespace (0=main, 1=talk, etc.)'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Maximum number of pages to export'
    )
    
    args = parser.parse_args()
    
    # Load environment variables if dotenv is available
    if load_dotenv:
        load_dotenv()
    
    # Run scraper
    scrape_mediawiki(
        wiki_url=args.url,
        wiki_path=args.path,
        output_dir=args.output,
        username=args.username,
        password=args.password,
        namespace=args.namespace,
        limit=args.limit
    )


if __name__ == '__main__':
    main()
