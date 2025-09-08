"""Enhanced error handling and retry logic."""
import time
import requests
from typing import Callable, Any, Optional
from rich.console import Console

class RetryHandler:
    """Handle retries for API calls with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.console = Console()
    
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic and exponential backoff."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except (requests.RequestException, ConnectionError, TimeoutError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    self.console.print(f"[yellow]Connection failed, retrying in {delay:.1f}s... (attempt {attempt + 1}/{self.max_retries})[/yellow]")
                    time.sleep(delay)
                else:
                    self.console.print(f"[red]Failed after {self.max_retries} attempts.[/red]")
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operation cancelled by user.[/yellow]")
                raise
            except Exception as e:
                # For non-network errors, don't retry
                raise e
        
        # If we get here, all retries failed
        raise last_exception

class NetworkChecker:
    """Check network connectivity."""
    
    @staticmethod
    def is_connected(url: str = "https://api.groq.com", timeout: int = 5) -> bool:
        """Check if we can reach the API endpoint."""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code < 500
        except:
            return False
