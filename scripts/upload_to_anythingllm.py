#!/usr/bin/env python3
"""
AnythingLLM Document Uploader
Uploads documents to AnythingLLM and embeds them in a workspace.
"""

import os
import sys
import argparse
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests is required. Install with: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables only.")
    load_dotenv = None


class AnythingLLMClient:
    """Client for AnythingLLM API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
    
    def ping(self) -> bool:
        """Check if AnythingLLM is reachable."""
        try:
            resp = requests.get(f'{self.base_url}/api/ping', timeout=10)
            return resp.status_code == 200
        except Exception as e:
            print(f"Ping failed: {e}")
            return False
    
    def get_workspaces(self) -> list:
        """Get all workspaces."""
        try:
            resp = requests.get(
                f'{self.base_url}/api/v1/workspaces',
                headers=self.headers,
                timeout=30
            )
            resp.raise_for_status()
            return resp.json().get('workspaces', [])
        except Exception as e:
            print(f"Error getting workspaces: {e}")
            return []
    
    def create_workspace(self, name: str) -> dict:
        """Create a new workspace."""
        try:
            resp = requests.post(
                f'{self.base_url}/api/v1/workspace/new',
                headers=self.headers,
                json={'name': name},
                timeout=30
            )
            resp.raise_for_status()
            return resp.json().get('workspace', {})
        except Exception as e:
            print(f"Error creating workspace: {e}")
            return {}
    
    def upload_document(self, file_path: Path) -> dict:
        """Upload a document to AnythingLLM."""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'text/plain')}
                resp = requests.post(
                    f'{self.base_url}/api/v1/document/upload',
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    files=files,
                    timeout=60
                )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error uploading {file_path.name}: {e}")
            return {}
    
    def add_document_to_workspace(self, workspace_slug: str, document_location: str) -> bool:
        """Add an uploaded document to a workspace for embedding."""
        try:
            resp = requests.post(
                f'{self.base_url}/api/v1/workspace/{workspace_slug}/update-embeddings',
                headers=self.headers,
                json={'adds': [document_location], 'deletes': []},
                timeout=120
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"Error adding document to workspace: {e}")
            return False


def upload_documents(
    anythingllm_url: str,
    api_key: str,
    documents_dir: str,
    workspace_name: str = "MediaWiki Import"
):
    """
    Upload documents to AnythingLLM and embed them in a workspace.
    
    Args:
        anythingllm_url: AnythingLLM server URL
        api_key: API key for authentication
        documents_dir: Directory containing documents to upload
        workspace_name: Name of the workspace to use/create
    """
    print(f"Connecting to AnythingLLM at {anythingllm_url}...")
    
    client = AnythingLLMClient(anythingllm_url, api_key)
    
    # Check connection
    if not client.ping():
        print("Error: Cannot connect to AnythingLLM. Is it running?")
        sys.exit(1)
    print("Connected successfully!")
    
    # Find or create workspace
    print(f"\nLooking for workspace '{workspace_name}'...")
    workspaces = client.get_workspaces()
    workspace = None
    
    for ws in workspaces:
        if ws.get('name') == workspace_name:
            workspace = ws
            break
    
    if workspace:
        print(f"Found existing workspace: {workspace_name}")
    else:
        print(f"Creating new workspace: {workspace_name}")
        workspace = client.create_workspace(workspace_name)
        if not workspace:
            print("Error: Failed to create workspace")
            sys.exit(1)
    
    workspace_slug = workspace.get('slug')
    print(f"Workspace slug: {workspace_slug}")
    
    # Get documents to upload
    docs_path = Path(documents_dir)
    if not docs_path.exists():
        print(f"Error: Documents directory not found: {docs_path}")
        sys.exit(1)
    
    # Supported file extensions
    extensions = {'.txt', '.md', '.pdf', '.docx', '.doc', '.html', '.htm'}
    files = [f for f in docs_path.iterdir() if f.is_file() and f.suffix.lower() in extensions]
    
    if not files:
        print(f"No documents found in {docs_path}")
        sys.exit(1)
    
    print(f"\nFound {len(files)} documents to upload")
    
    # Upload documents
    uploaded = 0
    embedded = 0
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] Uploading: {file_path.name}")
        
        result = client.upload_document(file_path)
        if not result:
            continue
        
        uploaded += 1
        
        # Get the document location for embedding
        doc_location = result.get('documents', [{}])[0].get('location')
        if doc_location:
            print(f"  Embedding document...")
            if client.add_document_to_workspace(workspace_slug, doc_location):
                embedded += 1
                print(f"  ✓ Embedded successfully")
            else:
                print(f"  ✗ Embedding failed")
        
        # Rate limiting - brief pause between uploads
        time.sleep(0.5)
    
    # Summary
    print(f"\n{'='*50}")
    print("Upload Complete!")
    print(f"  - Documents uploaded: {uploaded}/{len(files)}")
    print(f"  - Documents embedded: {embedded}/{len(files)}")
    print(f"  - Workspace: {workspace_name}")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(
        description='Upload documents to AnythingLLM'
    )
    parser.add_argument(
        '--url', '-u',
        default=os.getenv('ANYTHINGLLM_URL', 'http://localhost:3001'),
        help='AnythingLLM URL (default: http://localhost:3001)'
    )
    parser.add_argument(
        '--api-key', '-k',
        default=os.getenv('ANYTHINGLLM_API_KEY'),
        help='AnythingLLM API key'
    )
    parser.add_argument(
        '--documents', '-d',
        default='./wiki_export',
        help='Directory containing documents to upload'
    )
    parser.add_argument(
        '--workspace', '-w',
        default='MediaWiki Import',
        help='Workspace name (default: MediaWiki Import)'
    )
    
    args = parser.parse_args()
    
    # Load environment variables if dotenv is available
    if load_dotenv:
        load_dotenv()
        # Re-read after loading .env
        if not args.api_key:
            args.api_key = os.getenv('ANYTHINGLLM_API_KEY')
    
    if not args.api_key:
        print("Error: API key is required.")
        print("Set ANYTHINGLLM_API_KEY environment variable or use --api-key")
        print("\nTo get an API key:")
        print("1. Open AnythingLLM in your browser")
        print("2. Go to Settings → Developer → API Keys")
        print("3. Create a new API key")
        sys.exit(1)
    
    upload_documents(
        anythingllm_url=args.url,
        api_key=args.api_key,
        documents_dir=args.documents,
        workspace_name=args.workspace
    )


if __name__ == '__main__':
    main()
