from django.contrib import admin

from .models import Message, Session


class MessageInline(admin.TabularInline):
    model = Message
    fields = ('role', 'content', 'created_at')
    readonly_fields = ('created_at',)
    extra = 0


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message_count', 'created_at')
    search_fields = ('user__email',)
    inlines = [MessageInline]
    readonly_fields = ('created_at',)

    def message_count(self, obj):
        return obj.messages.count()
