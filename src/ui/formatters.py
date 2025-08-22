"""UI formatters for text processing."""
import re
from typing import List, Dict, Any
from rich.text import Text
from rich.markdown import Markdown


class TextFormatter:
    """Utilities for formatting text content."""
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to specified length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def extract_code_blocks(text: str) -> List[Dict[str, str]]:
        """Extract code blocks from markdown text."""
        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        code_blocks = []
        for language, code in matches:
            code_blocks.append({
                'language': language or 'text',
                'code': code.strip()
            })
        
        return code_blocks
    
    @staticmethod
    def format_code_preview(code: str, max_lines: int = 5) -> str:
        """Format code for preview display."""
        lines = code.split('\n')
        if len(lines) <= max_lines:
            return code
        
        preview_lines = lines[:max_lines]
        remaining = len(lines) - max_lines
        preview_lines.append(f"... ({remaining} more lines)")
        
        return '\n'.join(preview_lines)
    
    @staticmethod
    def highlight_keywords(text: str, keywords: List[str], style: str = "bold yellow") -> Text:
        """Highlight specific keywords in text."""
        rich_text = Text(text)
        
        for keyword in keywords:
            # Find all occurrences of the keyword (case insensitive)
            start = 0
            while True:
                pos = text.lower().find(keyword.lower(), start)
                if pos == -1:
                    break
                
                rich_text.stylize(style, pos, pos + len(keyword))
                start = pos + len(keyword)
        
        return rich_text
    
    @staticmethod
    def clean_whitespace(text: str) -> str:
        """Clean excessive whitespace from text."""
        # Remove excessive newlines (more than 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove trailing whitespace from lines
        lines = text.split('\n')
        lines = [line.rstrip() for line in lines]
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes // 1024}KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes // (1024 * 1024)}MB"
        else:
            return f"{size_bytes // (1024 * 1024 * 1024)}GB"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            return f"{hours}h {remaining_minutes}m"


class MarkdownProcessor:
    """Enhanced markdown processing utilities."""
    
    @staticmethod
    def extract_tables(text: str) -> List[str]:
        """Extract markdown tables from text."""
        # Simple table detection pattern
        table_pattern = r'(\|.*\|[\r\n]+\|[-\s\|]+\|[\r\n]+(?:\|.*\|[\r\n]*)*)'
        tables = re.findall(table_pattern, text, re.MULTILINE)
        return tables
    
    @staticmethod
    def extract_headers(text: str) -> List[Dict[str, Any]]:
        """Extract headers from markdown text."""
        headers = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('# ').strip()
                headers.append({
                    'level': level,
                    'title': title,
                    'line': i + 1
                })
        
        return headers
    
    @staticmethod
    def extract_links(text: str) -> List[Dict[str, str]]:
        """Extract links from markdown text."""
        # Pattern for [text](url) links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, text)
        
        links = []
        for text_part, url in matches:
            links.append({
                'text': text_part,
                'url': url
            })
        
        return links
    
    @staticmethod
    def create_toc(headers: List[Dict[str, Any]]) -> str:
        """Create table of contents from headers."""
        if not headers:
            return ""
        
        toc_lines = ["# Table of Contents", ""]
        
        for header in headers:
            indent = "  " * (header['level'] - 1)
            title = header['title']
            # Create anchor link (simplified)
            anchor = title.lower().replace(' ', '-').replace('.', '').replace(',', '')
            toc_lines.append(f"{indent}- [{title}](#{anchor})")
        
        return '\n'.join(toc_lines)
