from django.contrib import admin
from .models import (
    Publication, Publisher, DeleteRequest, ActivityLog,
    PublicationTypeDict, CitationDatabaseDict, PublicationScopeDict,
    AuthorStatusDict, ReportingPeriodDict, ResultDict,
)


class ReferenceDictAdmin(admin.ModelAdmin):
    list_display = ['code', 'label', 'sort_order']
    search_fields = ['code', 'label']
    ordering = ['sort_order', 'code']


admin.site.register([PublicationTypeDict, CitationDatabaseDict, PublicationScopeDict,
                     AuthorStatusDict, ReportingPeriodDict, ResultDict], ReferenceDictAdmin)


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'year', 'department', 'status', 'owner', 'created_at']
    list_filter = ['status', 'department', 'year', 'result']
    search_fields = ['title', 'author', 'note']
    autocomplete_fields = ['department']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Основная информация', {
            'fields': ['title', 'author', 'year', 'department', 'result',
                       'publication_type', 'citation_db', 'publication_scope',
                       'author_status', 'reporting_period', 'reporting_year']
        }),
        ('Дополнительные поля', {
            'fields': ['publisher', 'circulation', 'head', 'executors', 'location', 'event_name',
                       'funding_source', 'volume', 'note', 'students_names',
                       'students_count', 'pages_count', 'printed_sheets',
                       'entry_month', 'event_date', 'keywords',
                       'doi', 'edn_code', 'elibrary_id']
        }),
        ('Системные поля', {
            'fields': ['owner', 'status', 'moderation_status', 'moderated_by',
                       'moderated_at', 'moderation_comment', 'is_archived',
                       'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'created_at']
    search_fields = ['name', 'city']


@admin.register(DeleteRequest)
class DeleteRequestAdmin(admin.ModelAdmin):
    list_display = ['publication', 'requester', 'status', 'reviewed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['publication__title', 'requester__username', 'reason']
    readonly_fields = ['created_at', 'reviewed_at']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'publication', 'ip_address', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'publication__title']
    readonly_fields = ['user', 'action', 'publication', 'details', 'ip_address', 'timestamp']