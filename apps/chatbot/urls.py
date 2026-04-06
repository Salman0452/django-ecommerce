from django.urls import path

from .views import ChatHistoryView, ChatView

app_name = 'chatbot'

urlpatterns = [
	path('', ChatView.as_view(), name='chat'),
	path('history/', ChatHistoryView.as_view(), name='history'),
]