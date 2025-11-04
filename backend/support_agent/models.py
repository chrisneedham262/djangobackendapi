from django.db import models


class FAQ(models.Model):
    question = models.TextField(unique=True)
    answer = models.TextField()

    def __str__(self):
        return self.question


class ChatHistory(models.Model):
    user_id = models.CharField(max_length=255)
    question = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat with {self.user_id} at {self.timestamp}"
