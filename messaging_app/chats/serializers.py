""" serializers.py
"""
from rest_framework import serializers
from .models import CustomUser, Conversation, Message


class CustomUserSerializer(serializers.Serializer):
    user_id = serializers.CharField(read_only=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return "{} {}".format(obj.first_name, obj.last_name)

    def validate_email(self, email):
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('A user with this email exists.')
        return email

    def create(self, validated_data):
        return CustomUser.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.first_name  = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()
        return instance

class MessageSerializer(serializers.Serializer):
    message_id = serializers.UUIDField(read_only=True)
    sender = serializers.UUIDField()
    conversation = serializers.UUIDField()
    message_body =serializers.CharField()
    sent_at = serializers.DateTimeField(read_only=True)

    def validate_message_body(self, message):
        if not message.strip():
            raise serializers.ValidationError('Message body cannot be empty.')
        return message

    def create(self, validated_data):
        sender = CustomUser.objects.get(user_id=validated_data['sender'])
        conversation = Conversation.objects.get(conversation_id=validated_data['conversation'])

        message = Message.objects.create(
            sender=sender,
            conversation=conversation,
            message_body=validated_data['message_body']
        )
        return message


class ConversationSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField(read_only=True)
    participants = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    messages = MessageSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    latest_message = serializers.SerializerMethodField()

    def get_latest_message(self, obj):
        latest = obj.message.order_by('-sent_at').first()
        return latest.message_body if latest else None

    def create(self, validated_data):
        participant_ids = validated_data.pop('participants', [])
        conversation = Conversation.objects.create()
        users = CustomUser.objects.filter(user_id__in=participant_ids)
        conversation.participants.ser(users)
        return conversation
