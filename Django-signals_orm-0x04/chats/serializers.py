from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "bio"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    content = serializers.CharField()

    class Meta:
        model = Message
        fields = ["id", "sender", "conversation", "content", "timestamp"]

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    last_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "participants",
            "messages",
            "created_at",
            "last_message_preview",
        ]

    def get_last_message_preview(self, obj):
        last_msg = obj.messages.order_by("-timestamp").first()
        return last_msg.content[:50] if last_msg else "No messages yet."
