from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q
import re
from .models import Publication, DeleteRequest, ActivityLog, Publisher, Department, ResultType, CitationDatabase, PublicationType, PublicationScope, AuthorStatus, ReportingPeriod, Month, EntryStatus, ModerationStatus

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display', 'phone', 'department', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined']


# === Сериализаторы для справочников ===

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'code', 'full_name', 'short_name', 'description', 'email', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResultTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultType
        fields = ['id', 'name', 'display_name', 'description']
        read_only_fields = ['id']


class CitationDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CitationDatabase
        fields = ['id', 'code', 'name', 'description', 'website']
        read_only_fields = ['id']


class PublicationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicationType
        fields = ['id', 'code', 'name', 'description', 'is_active']
        read_only_fields = ['id']


class PublicationScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicationScope
        fields = ['id', 'code', 'name', 'description']
        read_only_fields = ['id']


class AuthorStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorStatus
        fields = ['id', 'code', 'name', 'description']
        read_only_fields = ['id']


class ReportingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingPeriod
        fields = ['id', 'code', 'name', 'display_order', 'is_active']
        read_only_fields = ['id']


class MonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Month
        fields = ['id', 'number', 'name', 'short_name']
        read_only_fields = ['id']


class EntryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryStatus
        fields = ['id', 'code', 'name', 'description', 'color']
        read_only_fields = ['id']


class ModerationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationStatus
        fields = ['id', 'code', 'name', 'description', 'color']
        read_only_fields = ['id']


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'city', 'country', 'website', 'email', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PublicationListSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    status = EntryStatusSerializer(read_only=True)
    moderation_status_rel = ModerationStatusSerializer(read_only=True)
    citation_db = CitationDatabaseSerializer(read_only=True)
    publication_type = PublicationTypeSerializer(read_only=True)
    publication_scope = PublicationScopeSerializer(read_only=True)
    author_status = AuthorStatusSerializer(read_only=True)
    reporting_period = ReportingPeriodSerializer(read_only=True)
    moderated_by = UserSerializer(read_only=True)
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'author', 'year', 
            'department', 'result', 'citation_db',
            'publication_type', 'publication_scope',
            'author_status', 'reporting_period',
            'status', 'moderation_status_rel', 'moderated_by',
            'owner', 'created_at', 'is_archived'
        ]


class PublicationDetailSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    status = EntryStatusSerializer(read_only=True)
    result = ResultTypeSerializer(read_only=True)
    moderation_status_rel = ModerationStatusSerializer(read_only=True)
    moderated_by = UserSerializer(read_only=True)
    citation_db = CitationDatabaseSerializer(read_only=True)
    publication_type = PublicationTypeSerializer(read_only=True)
    publication_scope = PublicationScopeSerializer(read_only=True)
    author_status = AuthorStatusSerializer(read_only=True)
    reporting_period = ReportingPeriodSerializer(read_only=True)
    entry_month = MonthSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'author', 'head', 'executors',
            'location', 'event_name', 'funding_source', 'volume', 'note',
            'students_names', 'year', 'students_count', 'pages_count',
            'result', 'citation_db',
            'department',
            'publication_type', 'publication_scope',
            'author_status',
            'pages_count', 'printed_sheets', 'circulation',
            'doi', 'edn_code', 'elibrary_id',
            'reporting_period', 'reporting_year',
            'entry_month', 'event_date', 'status',
            'moderation_status_rel', 'moderated_by', 
            'moderated_at', 'moderation_comment', 'is_archived',
            'owner', 'created_at', 'updated_at', 'publisher'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'moderated_by', 'moderated_at']


class PublicationCreateSerializer(serializers.ModelSerializer):
    circulation = serializers.CharField(required=False, allow_blank=True, default='0')
    
    class Meta:
        model = Publication
        fields = [
            'title', 'author', 'head', 'executors',
            'location', 'event_name', 'funding_source', 'volume', 'note',
            'students_names', 'year', 'students_count', 'pages_count',
            'result', 'citation_db', 'department', 'entry_month', 'event_date',
            'publication_type', 'publication_scope', 'author_status',
            'publisher', 'printed_sheets', 'circulation',
            'doi', 'edn_code', 'elibrary_id',
            'reporting_period', 'reporting_year'
        ]
    
    def to_internal_value(self, data):
        # Convert circulation string to int before processing
        if 'circulation' in data and isinstance(data['circulation'], str):
            if data['circulation'] == '' or data['circulation'] == 'undefined' or data['circulation'] == 'null':
                data['circulation'] = 0
            else:
                try:
                    data['circulation'] = int(data['circulation'])
                except (ValueError, TypeError):
                    data['circulation'] = 0
        return super().to_internal_value(data)
    
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
        
        # Handle integer fields that come as empty strings
        int_fields = ['students_count', 'pages_count', 'circulation']
        for field in int_fields:
            val = attrs.get(field)
            if val is None or val == '' or val == 'undefined' or val == 'null':
                attrs[field] = 0
            else:
                try:
                    attrs[field] = int(val)
                except (ValueError, TypeError):
                    attrs[field] = 0
        
        # Validate foreign key relations exist
        for field_name in ['result', 'citation_db', 'publication_type', 'publication_scope', 
                           'author_status', 'reporting_period', 'department', 'entry_month', 'publisher']:
            if field_name in attrs and attrs[field_name] is not None:
                # Just ensure the object exists - DRF will handle type validation
                pass
        
        if publication_type and author_status:
            # Check if both are objects with code attributes
            pub_type_code = getattr(publication_type, 'code', str(publication_type))
            author_status_code = getattr(author_status, 'code', str(author_status))
            
            if pub_type_code == 'student_article' and author_status_code == 'student':
                if not head:
                    raise serializers.ValidationError({
                        'head': 'Для студенческой статьи требуется научный руководитель'
                    })
        
        return super().validate(attrs)
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        user = self.context['request'].user
        if user.role == 'ADMIN':
            # Statuses will be set by model save() method
            pass
        else:
            # Statuses will be set by model save() method
            pass
        return super().create(validated_data)


class PublicationUpdateSerializer(serializers.ModelSerializer):
    circulation = serializers.CharField(required=False, allow_blank=True, default='0')
    
    class Meta:
        model = Publication
        fields = [
            'title', 'author', 'head', 'executors',
            'location', 'event_name', 'funding_source', 'volume', 'note',
            'students_names', 'year', 'students_count', 'pages_count',
            'result', 'citation_db', 'department', 'entry_month', 'event_date',
            'publication_type', 'publication_scope', 'author_status',
            'publisher', 'printed_sheets', 'circulation',
            'doi', 'edn_code', 'elibrary_id',
            'reporting_period', 'reporting_year'
        ]
    
    def to_internal_value(self, data):
        if 'circulation' in data and isinstance(data['circulation'], str):
            if data['circulation'] == '' or data['circulation'] == 'undefined' or data['circulation'] == 'null':
                data['circulation'] = 0
            else:
                try:
                    data['circulation'] = int(data['circulation'])
                except (ValueError, TypeError):
                    data['circulation'] = 0
        return super().to_internal_value(data)
    
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
        int_fields = ['students_count', 'pages_count', 'circulation']
        for field in int_fields:
            val = attrs.get(field)
            if val is None or val == '' or val == 'undefined' or val == 'null':
                attrs[field] = 0
            else:
                try:
                    attrs[field] = int(val)
                except (ValueError, TypeError):
                    attrs[field] = 0
        
        choice_fields = ['result', 'citation_db', 'publication_type', 
                         'publication_scope', 'reporting_period']
        for field in choice_fields:
            if field in attrs and attrs[field] == '':
                if field == 'result':
                    attrs[field] = ''
                else:
                    attrs[field] = None
        
        return super().validate(attrs)


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


class DeleteRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeleteRequest
        fields = ['status']
    
    def validate_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Статус должен быть 'approved' или 'rejected'")
        return value
    
    def update(self, instance, validated_data):
        validated_data['reviewed_by'] = self.context['request'].user
        validated_data['reviewed_at'] = timezone.now()
        return super().update(instance, validated_data)


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


from django.utils import timezone
