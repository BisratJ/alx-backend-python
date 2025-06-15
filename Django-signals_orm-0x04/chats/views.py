from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.cache import cache_page

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        return self.queryset.filter(participants=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        conversation_id = self.request.query_params.get("conversation_id")

        if conversation_id:
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_id)
                if self.request.user not in conversation.participants.all():
                    return Message.objects.none()
                return Message.objects.filter(conversation=conversation)
            except Conversation.DoesNotExist:
                return Message.objects.none()

        # fallback to all messages where user is a participant
        return Message.objects.filter(conversation__participants=self.request.user)

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get("conversation")

        if conversation_id:
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_id)
                if request.user not in conversation.participants.all():
                    return Response(
                        {"detail": "You are not a participant in this conversation."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except Conversation.DoesNotExist:
                return Response(
                    {"detail": "Conversation not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return super().create(request, *args, **kwargs)

@cache_page(60)
def conversation_view(request, conversation_id):
    messages = Message.objects.filter(conversation_id=conversation_id)
    return render(request, "conversation.html", {"messages": messages})
