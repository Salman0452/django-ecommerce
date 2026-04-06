from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.chatbot.models import Message, Session
from apps.chatbot.services import add_message, get_groq_response, get_or_create_session
from apps.users.models import User


class ServiceTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='chat-user@example.com',
            username='chatuser',
            password='pass123',
        )


class TestGetOrCreateSession(ServiceTestBase):
    def test_get_or_create_session_for_user(self):
        session = get_or_create_session(user=self.user)
        self.assertIsInstance(session, Session)
        self.assertEqual(session.user, self.user)

        same_session = get_or_create_session(user=self.user)
        self.assertEqual(session.id, same_session.id)

    def test_get_or_create_session_for_anonymous(self):
        session = get_or_create_session(session_key='anon-session-1')
        self.assertIsNone(session.user)
        self.assertEqual(session.session_key, 'anon-session-1')

        same_session = get_or_create_session(session_key='anon-session-1')
        self.assertEqual(session.id, same_session.id)


class TestAddMessage(ServiceTestBase):
    def test_add_message_saves_message(self):
        session = get_or_create_session(user=self.user)
        message = add_message(session=session, role='user', content='Hello!')

        self.assertEqual(message.session, session)
        self.assertEqual(message.role, 'user')
        self.assertEqual(message.content, 'Hello!')
        self.assertEqual(Message.objects.filter(session=session).count(), 1)


@override_settings(GROQ_API_KEY='test-api-key', GROQ_MODEL='test-model')
class TestGetGroqResponse(ServiceTestBase):
    @patch('apps.chatbot.services.Groq')
    def test_get_groq_response_saves_messages_and_returns_text(self, groq_cls):
        session = get_or_create_session(user=self.user)

        mock_completion = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content='Try our featured electronics products!')
                )
            ]
        )
        groq_client = groq_cls.return_value
        groq_client.chat.completions.create.return_value = mock_completion

        response = get_groq_response(session=session, user_message='What should I buy?')

        self.assertEqual(response, 'Try our featured electronics products!')

        messages = list(Message.objects.filter(session=session).values_list('role', 'content'))
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0], ('user', 'What should I buy?'))
        self.assertEqual(messages[1], ('assistant', 'Try our featured electronics products!'))

        groq_client.chat.completions.create.assert_called_once()
        call_kwargs = groq_client.chat.completions.create.call_args.kwargs
        self.assertEqual(call_kwargs['model'], 'test-model')
        self.assertEqual(call_kwargs['messages'][0]['role'], 'system')
