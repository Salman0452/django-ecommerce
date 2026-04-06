from django.conf import settings
from groq import Groq

from .models import Message, Session


SYSTEM_PROMPT = (
    "You are a helpful shopping assistant for an e-commerce store. "
    "Help users find products, answer questions about orders, and provide shopping advice."
)


def get_or_create_session(user=None, session_key=None):
    """Return a chatbot session for an authenticated user or anonymous session key."""
    if user and getattr(user, 'is_authenticated', False):
        session, _ = Session.objects.get_or_create(user=user)
        return session

    if not session_key:
        raise ValueError('A session_key is required for anonymous sessions.')

    session, _ = Session.objects.get_or_create(user=None, session_key=session_key)
    return session


def add_message(session, role, content):
    """Persist a single chat message for a session."""
    return Message.objects.create(session=session, role=role, content=content)


def get_session_messages(session):
    """Return ordered session messages."""
    return session.messages.all()


def get_groq_response(session, user_message):
    """Send conversation context to Groq, persist user and assistant messages, return text."""
    add_message(session=session, role='user', content=user_message)

    history = get_session_messages(session)
    llm_messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    llm_messages.extend(
        {'role': message.role, 'content': message.content}
        for message in history
    )

    client = Groq(api_key=settings.GROQ_API_KEY)
    completion = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=llm_messages,
    )
    assistant_text = completion.choices[0].message.content.strip()

    add_message(session=session, role='assistant', content=assistant_text)
    return assistant_text
