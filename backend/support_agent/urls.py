from django.urls import path
from .views import customer_support_agent

urlpatterns = [
    path("ask/", customer_support_agent, name="customer_support_agent"),
]
