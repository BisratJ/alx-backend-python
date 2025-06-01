""" models.py: Defines custom user, conversations, and messaging models.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """A user model which is an extension of the Abstract user."""
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=80, blank=True, unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name =  models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15, blank=True,null=True)


class Conversation(models.Model):
    """A model that tracks which users are involved in a conversation."""
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(CustomUser, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    """ A model that define messaging between users."""
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
