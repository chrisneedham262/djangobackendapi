import requests
import os
from django.conf import settings
from support_agent.models import FAQ
from rapidfuzz import process, fuzz


def search_faq(query):
    """Find the best-matching FAQ using fuzzy search (Levenshtein Distance)."""
    try:
        # Get all FAQ entries
        faq_list = list(FAQ.objects.values_list("question", "answer"))

        if not faq_list:
            print("🛑 No FAQs found in the database.")
            return None  # No FAQs exist

        # ✅ Find the best match (fix: use fuzz.ratio correctly)
        best_match = process.extractOne(
            query, [faq[0] for faq in faq_list], scorer=fuzz.ratio
        )

        if best_match:
            matched_question, similarity_score = best_match[0], best_match[1]
            print(
                f"✅ Best Match Found: {matched_question} (Similarity: {similarity_score}%)"
            )

            # ✅ If similarity score is high enough, return the corresponding FAQ answer
            if similarity_score > 60:  # 60% threshold for best match
                matched_answer = next(
                    (faq[1] for faq in faq_list if faq[0] == matched_question), None
                )
                print(f"✅ Matched FAQ Answer: {matched_answer}")
                return matched_answer

        print("🛑 No sufficiently similar FAQ found.")
        return None  # No close enough match found

    except Exception as e:
        print(f"❌ Error in FAQ matching: {e}")
        return None


def read_knowledge_file():
    """Read the markdown knowledge file"""
    knowledge_path = os.path.join(settings.BASE_DIR, "knowledge", "company_knowledge.md")
    
    if not os.path.exists(knowledge_path):
        return None
        
    try:
        with open(knowledge_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading knowledge file: {e}")
        return None

def generate_response_with_llm(query, faq_answer=None):
    """Use GPT-4 or Ollama to refine the FAQ answer or generate a new response."""
    try:
        # Always read knowledge file
        knowledge_content = read_knowledge_file()
        
        if faq_answer:
            print(f"📝 Using FAQ Answer for Query: {query} → {faq_answer}")
            prompt = f"""You are a professional AI customer support assistant.
A customer asked: '{query}'.
Here is the correct FAQ answer: '{faq_answer}'.
Please rewrite this answer in a polite, natural, and engaging way."""
        elif knowledge_content:
            print(f"📄 Using Knowledge Document for Query: {query}")
            prompt = f"""You are a professional AI customer support assistant for our company.
A customer asked: '{query}'.

Here is our company knowledge base:
{knowledge_content}

Please provide a helpful, concise answer based ONLY on the information in the knowledge base above. If the information isn't in the knowledge base, politely say so."""
        else:
            print(f"⚠️ No FAQ or knowledge found for: {query}. Generating general response.")
            prompt = f"""A customer asked: '{query}'.
No specific information exists for this question. Please generate a helpful response and offer to connect them with support."""

        if settings.USE_OLLAMA:
            print("🤖 Using Ollama...")
            ollama_url = "http://localhost:11434/api/generate"
            data = {"model": "mistral", "prompt": prompt}
            response = requests.post(ollama_url, json=data).json()
            return response["response"].strip()
        else:
            print("🤖 Using OpenAI...")
            if not settings.OPENAI_API_KEY:
                print("❌ No OpenAI API key found!")
                return "Sorry, the AI service is not configured. Please contact support."
                
            openai_url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
            data = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a friendly AI customer support agent. Provide concise, helpful answers.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 300,
            }
            print(f"📤 Sending request to OpenAI...")
            response = requests.post(openai_url, json=data, headers=headers)
            response_json = response.json()
            
            if response.status_code != 200:
                print(f"❌ OpenAI Error: {response_json}")
                return "Sorry, I'm having trouble connecting to the AI service. Please try again."
            
            answer = response_json["choices"][0]["message"]["content"].strip()
            print(f"✅ Got response from OpenAI: {answer[:100]}...")
            return answer

    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return (
            faq_answer
            if faq_answer
            else "I'm sorry, but I encountered an error. Please try again."
        )
