"""
OpenAI Agent with built-in rate limiting
"""
import time
import os
from openai import OpenAI
from django.conf import settings

# Rate limiting state
_last_request_time = 0
_min_request_interval = 0.1  # seconds (OpenAI has more generous limits)


def ask_openai(prompt, model="gpt-3.5-turbo", temperature=0.4, max_tokens=1024):
    """
    Send a request to OpenAI API with built-in rate limiting.
    
    Args:
        prompt (str): The prompt to send to OpenAI
        model (str): The OpenAI model to use (default: gpt-3.5-turbo)
        temperature (float): Temperature setting (default: 0.4)
        max_tokens (int): Maximum tokens in response (default: 1024)
    
    Returns:
        str: OpenAI's response text
        
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
    
    # Initialize OpenAI client
    api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in settings or environment variables")
    
    client = OpenAI(api_key=api_key)
    
    try:
        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Update last request time
        _last_request_time = time.time()
        
        # Extract and return the text content
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")


def ask_openai_dev(prompt, temperature=0.3, max_tokens=2048):
    """
    OpenAI Dev agent - world-class AI specializing in Django, Next.js, and AI agent architecture
    
    Args:
        prompt (str): The coding question or task
        temperature (float): Temperature setting (default: 0.3)
        max_tokens (int): Maximum tokens in response (default: 2048)
    
    Returns:
        str: OpenAI's response
    """
    system_prompt = """You are a world-class AI specializing in Django, Next.js, and AI agent architecture. 
Provide professional, concise answers. Focus on clean and scalable code. Always include brief explanations and comments when helpful."""
    
    full_prompt = f"{system_prompt}\n\n{prompt}"
    
    return ask_openai(
        prompt=full_prompt,
        model="gpt-4-turbo",
        temperature=temperature,
        max_tokens=max_tokens
    )


def ask_openai_assistant(prompt, temperature=0.4, max_tokens=1024):
    """
    OpenAI Assistant - smart coding assistant for small tasks, debugging, and fast answers
    
    Args:
        prompt (str): The task to process
        temperature (float): Temperature setting (default: 0.4)
        max_tokens (int): Maximum tokens in response (default: 1024)
    
    Returns:
        str: OpenAI's response
    """
    system_prompt = """You are a smart coding assistant specialized in small tasks, debugging, and fast answers. 
Prioritize speed and helpfulness over formality. Focus on simple and practical solutions."""
    
    full_prompt = f"{system_prompt}\n\n{prompt}"
    
    return ask_openai(
        prompt=full_prompt,
        model="gpt-3.5-turbo",
        temperature=temperature,
        max_tokens=max_tokens
    )

