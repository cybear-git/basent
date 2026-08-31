from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
import re

from .models import (
    Publication, Publisher, DeleteRequest, ActivityLog,
    PublicationTypeDict, CitationDatabaseDict, PublicationScopeDict,
    AuthorStatusDict, ReportingPeriodDict, ResultDict,
)
from users.models import Department

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display', 'phone', 'department', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined']


class PublicationReferenceFieldsMixin:
    """Миксин: справочные FK сериализуются кодом + дополнительным *_display полем."""

    department = serializers.SlugRelatedField(slug_field='code', read_only=True)
    publication_type = serializers.SlugRelatedField(slug_field='code', read_only=True)
    citation_db = serializers.SlugRelatedField(slug_field='code', read_only=True)
    publication_scope = serializers.SlugRelatedField(slug_field='code', read_only=True)
    author_status = serializers.SlugRelatedField(slug_field='code', read_only=True)
    reporting_period = serializers.SlugRelatedField(slug_field='code', read_only=True)
    result = serializers.SlugRelatedField(slug_field='code', read_only=True)

    def get_department_display(self, obj):
        return obj.department.full_name if obj.department else ''

    def get_publication_type_display(self, obj):
        return obj.publication_type.label if obj.publication_type else ''

    def get_citation_db_display(self, obj):
        return obj.citation_db.label if obj.citation_db else ''

    def get_publication_scope_display(self, obj):
        return obj.publication_scope.label if obj.publication_scope else ''

    def get_author_status_display(self, obj):
        return obj.author_status.label if obj.author_status else ''

    def get_reporting_period_display(self, obj):
        return obj.reporting_period.label if obj.reporting_period else ''

    def get_result_display(self, obj):
        return obj.result.label if obj.result else ''


class PublicationListSerializer(PublicationReferenceFieldsMixin, serializers.ModelSerializer):
    department_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    moderation_status_display = serializers.CharField(source='get_moderation_status_display', read_only=True)
    moderated_by_username = serializers.CharField(source='moderated_by.username', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    citation_db_display = serializers.SerializerMethodField()
    publication_type_display = serializers.SerializerMethodField()
    publication_scope_display = serializers.SerializerMethodField()
    author_status_display = serializers.SerializerMethodField()
    reporting_period_display = serializers.SerializerMethodField()
    result_display = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'author', 'year', 'department', 'department_display',
            'result', 'result_display',
            'citation_db', 'citation_db_display',
            'publication_type', 'publication_type_display',
            'publication_scope', 'publication_scope_display',
            'author_status', 'author_status_display',
            'reporting_period', 'reporting_period_display',
            'status', 'status_display',
            'moderation_status', 'moderation_status_display', 'moderated_by_username',
            'owner_username', 'created_at', 'is_archived'
        ]


class PublicationDetailSerializer(PublicationReferenceFieldsMixin, serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    department_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    result_display = serializers.SerializerMethodField()
    moderation_status_display = serializers.CharField(source='get_moderation_status_display', read_only=True)
    moderated_by = UserSerializer(read_only=True)
    citation_db_display = serializers.SerializerMethodField()
    publication_type_display = serializers.SerializerMethodField()
    publication_scope_display = serializers.SerializerMethodField()
    author_status_display = serializers.SerializerMethodField()
    reporting_period_display = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'author', 'head', 'executors',
            'location', 'event_name', 'funding_source', 'volume', 'note',
            'students_names', 'year', 'students_count', 'pages_count',
            'result', 'result_display',
            'citation_db', 'citation_db_display',
            'department', 'department_display',
            'publication_type', 'publication_type_display',
            'publication_scope', 'publication_scope_display',
            'author_status', 'author_status_display',
            'printed_sheets', 'circulation',
            'doi', 'edn_code', 'elibrary_id',
            'reporting_period', 'reporting_period_display', 'reporting_year',
            'entry_month', 'event_date', 'status', 'status_display',
            'moderation_status', 'moderation_status_display', 'moderated_by',
            'moderated_at', 'moderation_comment', 'is_archived',
            'owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'moderated_by', 'moderated_at']


class PublicationWriteSerializerMixin:
    """Общая логика для create/update сериализаторов."""

    FILLED_CHOICE_FIELDS = (
        'result', 'citation_db', 'publication_type',
        'publication_scope', 'reporting_period', 'author_status',
    )

    def _normalize(self, data):
        data = dict(data)
        for field in ['circulation', 'students_count', 'pages_count']:
            if field in data:
                value = data[field]
                if value in (None, '') or (isinstance(value, str) and value.strip() in ('', 'undefined', 'null')):
                    data[field] = 0
                elif isinstance(value, str):
                    try:
                        data[field] = int(value)
                    except (ValueError, TypeError):
                        data[field] = 0
        if 'printed_sheets' in data:
            value = data['printed_sheets']
            if value in (None, '') or (isinstance(value, str) and value.strip() in ('', 'undefined', 'null')):
                data['printed_sheets'] = 0
            elif isinstance(value, str):
                try:
                    data['printed_sheets'] = float(value.replace(',', '.'))
                except (ValueError, TypeError):
                    data['printed_sheets'] = 0
        if 'year' in data:
            value = data['year']
            if isinstance(value, str):
                try:
                    data['year'] = int(value) if value.strip() else None
                except (ValueError, TypeError):
                    data['year'] = None
            elif isinstance(value, float) and (value != value or value != int(value)):
                data['year'] = int(value) if value == value else None
        if 'entry_month' in data:
            value = data['entry_month']
            if isinstance(value, str):
                try:
                    data['entry_month'] = int(value) if value.strip() else None
                except (ValueError, TypeError):
                    data['entry_month'] = None
        for field in self.FILLED_CHOICE_FIELDS + ('department',):
            if field in data and data[field] in (None, ''):
                data[field] = None
        return data

    def validate_edn_code(self, value):
        if value:
            if not re.match(r'^[A-Z0-9]{6}$', value.upper()):
                raise serializers.ValidationError("EDN код должен состоять из 6 заглавных букв или цифр")
        return value.upper() if value else value

    def validate_doi(self, value):
        if value:
            if not value.startswith('10.'):
                raise serializers.ValidationError("DOI должен начинаться с '10.'")
        return value

    def validate(self, attrs):
        publication_type = attrs.get('publication_type')
        author_status = attrs.get('author_status')
        head = attrs.get('head')

        if (
            publication_type and publication_type.code == 'student_article'
            and author_status and author_status.code == 'student'
            and not head
        ):
            raise serializers.ValidationError({
                'head': 'Для студенческой статьи требуется научный руководитель'
            })

        return super().validate(attrs)


class PublicationCreateSerializer(PublicationWriteSerializerMixin, serializers.ModelSerializer):
    department = serializers.SlugRelatedField(
        slug_field='code', queryset=Department.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Кафедра с таким кодом не найдена'}
    )
    result = serializers.SlugRelatedField(
        slug_field='code', queryset=ResultDict.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Некорректное значение результата'}
    )
    citation_db = serializers.SlugRelatedField(
        slug_field='code', queryset=CitationDatabaseDict.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Некорректное значение базы цитирования'}
    )
    publication_type = serializers.SlugRelatedField(
        slug_field='code', queryset=PublicationTypeDict.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Некорректное значение типа публикации'}
    )
    publication_scope = serializers.SlugRelatedField(
        slug_field='code', queryset=PublicationScopeDict.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Некорректное значение уровня публикации'}
    )
    author_status = serializers.SlugRelatedField(
        slug_field='code', queryset=AuthorStatusDict.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Некорректное значение статуса автора'}
    )
    reporting_period = serializers.SlugRelatedField(
        slug_field='code', queryset=ReportingPeriodDict.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Некорректное значение отчётного периода'}
    )
    publisher = serializers.PrimaryKeyRelatedField(
        queryset=Publisher.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Publication
        fields = [
            'title', 'author', 'head', 'executors',
            'location', 'event_name', 'funding_source', 'volume', 'note',
            'students_names', 'keywords', 'year', 'students_count', 'pages_count',
            'result', 'citation_db', 'department', 'entry_month', 'event_date',
            'publication_type', 'publication_scope', 'author_status',
            'publisher', 'printed_sheets', 'circulation',
            'doi', 'edn_code', 'elibrary_id',
            'reporting_period', 'reporting_year'
        ]

    def to_internal_value(self, data):
        data = self._normalize(data)
        return super().to_internal_value(data)

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        user = self.context['request'].user
        if user.role == 'ADMIN':
            validated_data['status'] = 'active'
            validated_data['moderation_status'] = 'approved'
        else:
            validated_data['status'] = 'active'
            validated_data['moderation_status'] = 'pending'
        return super().create(validated_data)


class PublicationUpdateSerializer(PublicationWriteSerializerMixin, serializers.ModelSerializer):
    department = serializers.SlugRelatedField(
        slug_field='code', queryset=Department.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Кафедра с таким кодом не найдена'}
    )
    result = serializers.SlugRelatedField(
        slug_field='code', queryset=ResultDict.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Некорректное значение результата'}
    )
    citation_db = serializers.SlugRelatedField(
        slug_field='code', queryset=CitationDatabaseDict.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Некорректное значение базы цитирования'}
    )
    publication_type = serializers.SlugRelatedField(
        slug_field='code', queryset=PublicationTypeDict.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Некорректное значение типа публикации'}
    )
    publication_scope = serializers.SlugRelatedField(
        slug_field='code', queryset=PublicationScopeDict.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Некорректное значение уровня публикации'}
    )
    author_status = serializers.SlugRelatedField(
        slug_field='code', queryset=AuthorStatusDict.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Некорректное значение статуса автора'}
    )
    reporting_period = serializers.SlugRelatedField(
        slug_field='code', queryset=ReportingPeriodDict.objects.all(), required=False, allow_null=True,
        error_messages={'does_not_exist': 'Некорректное значение отчётного периода'}
    )
    publisher = serializers.PrimaryKeyRelatedField(
        queryset=Publisher.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Publication
        fields = [
            'title', 'author', 'head', 'executors',
            'location', 'event_name', 'funding_source', 'volume', 'note',
            'students_names', 'keywords', 'year', 'students_count', 'pages_count',
            'result', 'citation_db', 'department', 'entry_month', 'event_date',
            'publication_type', 'publication_scope', 'author_status',
            'publisher', 'printed_sheets', 'circulation',
            'doi', 'edn_code', 'elibrary_id',
            'reporting_period', 'reporting_year'
        ]

    def to_internal_value(self, data):
        data = self._normalize(data)
        return super().to_internal_value(data)


class PublicationModerateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected'])
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class DeleteRequestSerializer(serializers.ModelSerializer):
    requester_username = serializers.CharField(source='requester.username', read_only=True)
    publication_title = serializers.CharField(source='publication.title', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = DeleteRequest
        fields = [
            'id', 'publication', 'publication_title', 'requester', 'requester_username',
            'reason', 'status', 'status_display', 'reviewed_by', 'reviewed_by_username',
            'reviewed_at', 'created_at'
        ]
        read_only_fields = ['id', 'requester', 'status', 'reviewed_by', 'reviewed_at', 'created_at']


class DeleteRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeleteRequest
        fields = ['publication', 'reason']

    def create(self, validated_data):
        validated_data['requester'] = self.context['request'].user
        return super().create(validated_data)


class ActivityLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    publication_title = serializers.CharField(source='publication.title', read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'user_username', 'action', 'action_display',
            'publication', 'publication_title', 'details', 'ip_address', 'timestamp'
        ]