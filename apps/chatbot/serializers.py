from rest_framework import serializers

from .models import Message, Session


class MessageSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Message
        fields = ['role', 'content', 'createdAt']


class ChatInputSerializer(serializers.Serializer):
    message = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)


class SessionSerializer(serializers.ModelSerializer):
    sessionId = serializers.CharField(source='id', read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = ['sessionId', 'messages']
