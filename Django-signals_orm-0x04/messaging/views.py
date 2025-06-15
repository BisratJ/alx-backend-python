from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter
from django.db.models import Prefetch

User = get_user_model()


def get_thread(message):
    """
    Recursively retrieves a message and all of its replies in a flat list.
    """
    thread = [message]
    for reply in message.replies.all().order_by("sent_at"):
        thread.extend(get_thread(reply))
    return thread


@login_required
def delete_user(request):
    """
    Deletes the currently logged-in user's account and all related data.
    """
    user = request.user
    user.delete()
    return redirect("account_deleted")


@login_required
def unread_messages_view(request):
    """
    Displays unread messages for the logged-in user.
    """
    messages = Message.unread.unread_for_user(request.user)
    return render(request, "inbox.html", {"messages": messages})


replies_prefetch = Prefetch(
    "replies",
    queryset=Message.objects.select_related("sender").only(
        "id", "content", "sender__username", "sent_at"
    ),
)

@login_required
def message_edit_history(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    history = message.history.select_related("edited_by").all()
    return render(
        request, "messaging/edit_history.html", {"message": message, "history": history}
    )


@cache_page(60)
def conversation_view(request, conversation_id):
    """
    Caches and displays all messages in a conversation.
    """
    messages = (
        Message.objects.filter(conversation_id=conversation_id)
        .select_related("sender")
        .only("content", "sender__username", "sent_at")
        .prefetch_related("replies")
    )
    return render(request, "conversation.html", {"messages": messages})


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
                return (
                    Message.objects.filter(conversation=conversation)
                    .select_related("sender")
                    .prefetch_related(
                        Prefetch(
                            "replies",
                            queryset=Message.objects.select_related("sender","receiver").only(
                                "id", "content", "sender__username", "sent_at"
                            ),
                        )
                    )
                )
            except Conversation.DoesNotExist:
                return Message.objects.none()

        return Message.objects.select_related("sender").prefetch_related("replies")

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
