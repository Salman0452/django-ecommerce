from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ChatInputSerializer, SessionSerializer
from .services import get_groq_response, get_or_create_session


class ChatView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ChatInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.session.session_key is None:
            request.session.create()

        user = request.user if request.user.is_authenticated else None
        chat_session = get_or_create_session(
            user=user,
            session_key=request.session.session_key,
        )

        response_text = get_groq_response(
            session=chat_session,
            user_message=serializer.validated_data['message'],
        )

        return Response(
            {
                'response': response_text,
                'sessionId': str(chat_session.id),
            },
            status=status.HTTP_200_OK,
        )


class ChatHistoryView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if request.session.session_key is None:
            request.session.create()

        user = request.user if request.user.is_authenticated else None
        chat_session = get_or_create_session(
            user=user,
            session_key=request.session.session_key,
        )

        serializer = SessionSerializer(chat_session)
        return Response(serializer.data, status=status.HTTP_200_OK)
