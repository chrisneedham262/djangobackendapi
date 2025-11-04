from rest_framework.response import Response
from rest_framework.decorators import api_view
from .utils import search_faq, generate_response_with_llm
from .models import ChatHistory
from .serializers import ChatHistorySerializer


@api_view(["POST"])
def customer_support_agent(request):
    user_id = request.data.get("user_id", "anonymous")
    query = request.data.get("query", "")

    # Step 1: Check if an FAQ answer exists
    faq_answer = search_faq(query)

    # Step 2: Generate a polished response using the LLM
    response = generate_response_with_llm(query, faq_answer)

    # Step 3: Save history
    chat_entry = ChatHistory.objects.create(
        user_id=user_id, question=query, response=response
    )
    serializer = ChatHistorySerializer(chat_entry)

    return Response(serializer.data)
