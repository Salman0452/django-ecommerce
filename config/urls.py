from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orders/', include('apps.orders.urls')),
    path('account/', include('apps.users.urls')),
    path('payments/', include('apps.payments.urls')),
    path('api/v1/chatbot/', include('apps.chatbot.urls')),
    # Products URLs use an empty prefix with <slug:slug>/ — keep last to avoid
    # shadowing other top-level prefixes.
    path('', include('apps.products.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )