"""
Claude Agent with built-in rate limiting
Rate limit: 1.3 seconds between requests
"""
import time
import os
from anthropic import Anthropic
from django.conf import settings

# Rate limiting state
_last_request_time = 0
_min_request_interval = 1.3  # seconds


def ask_claude(prompt, model="claude-3-sonnet-20240229", temperature=0.2, max_tokens=1024):
    """
    Send a request to Claude API with built-in rate limiting.
    
    Args:
        prompt (str): The prompt to send to Claude
        model (str): The Claude model to use (default: claude-3-sonnet-20240229)
        temperature (float): Temperature setting (default: 0.2)
        max_tokens (int): Maximum tokens in response (default: 1024)
    
    Returns:
        str: Claude's response text
        
    Raises:
        Exception: If API call fails
    """
    global _last_request_time
    
    # Enforce rate limiting
    current_time = time.time()
    time_since_last_request = current_time - _last_request_time
    
    if time_since_last_request < _min_request_interval:
        sleep_time = _min_request_interval - time_since_last_request
        time.sleep(sleep_time)
    
    # Initialize Anthropic client
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    
    client = Anthropic(api_key=api_key)
    
    try:
        # Make the API call
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Update last request time
        _last_request_time = time.time()
        
        # Extract and return the text content
        return response.content[0].text
        
    except Exception as e:
        raise Exception(f"Claude API error: {str(e)}")


def ask_claude_dev(prompt, temperature=0.3, max_tokens=2048):
    """
    Claude Dev agent - highly experienced full-stack engineer
    
    Args:
        prompt (str): The coding question or task
        temperature (float): Temperature setting (default: 0.3)
        max_tokens (int): Maximum tokens in response (default: 2048)
    
    Returns:
        str: Claude's response
    """
    system_prompt = """You are a highly experienced full-stack engineer working on a modular, scalable Django + Next.js project. 
Respond professionally. Write clean code. Always explain decisions. Add comments when needed. Follow best practices."""
    
    full_prompt = f"{system_prompt}\n\n{prompt}"
    
    return ask_claude(
        prompt=full_prompt,
        model="claude-3-opus-20240229",
        temperature=temperature,
        max_tokens=max_tokens
    )


def ask_claude_throttle(prompt, temperature=0.2, max_tokens=1024):
    """
    Claude Throttle agent - smart rate-limited assistant for summarization and data processing
    
    Args:
        prompt (str): The task to process
        temperature (float): Temperature setting (default: 0.2)
        max_tokens (int): Maximum tokens in response (default: 1024)
    
    Returns:
        str: Claude's response
    """
    system_prompt = """You are a smart rate-limited AI assistant focused on summarization and data processing. 
Never exceed request thresholds. Always respect rate limits. Provide concise, accurate responses."""
    
    full_prompt = f"{system_prompt}\n\n{prompt}"
    
    return ask_claude(
        prompt=full_prompt,
        model="claude-3-sonnet-20240229",
        temperature=temperature,
        max_tokens=max_tokens
    )

