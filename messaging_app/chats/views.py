from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import filters
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ViewSet):
    search_filter =filters.SearchFilter()

    def list(self, request: Request):
        queryset = Conversation.objects.all()

        queryset = self.search_filter.filter_queryset(request, queryset, self)

        serializer = ConversationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ViewSet):
    ordering_filter = filters.OrderingFilter()

    def list(self, request):
        queryset = Message.objects.all()

        queryset = self.ordering_filter.filter_queryset(request, queryset, self)

        serializer = MessageSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save()
            return Response(MessageSerializer(message), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
