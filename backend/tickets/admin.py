from django.contrib import admin

from .models import Category, SLA, Ticket, TicketAttachment, TicketComment, TicketHistory


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_agent')
    search_fields = ('name',)


@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = ('priority', 'response_hours', 'resolution_hours')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'priority', 'status', 'created_by', 'assigned_to', 'estimated_resolution')
    list_filter = ('status', 'priority', 'category', 'assigned_to')
    search_fields = ('title', 'description', 'created_by__username', 'assigned_to__username')
    readonly_fields = ('created_at', 'updated_at', 'resolved_at', 'closed_at')
    inlines = (TicketAttachmentInline, TicketCommentInline)


@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'actor', 'action', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('action', 'ticket__title')
