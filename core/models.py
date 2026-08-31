from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime
from django.conf import settings


def current_year():
    return datetime.date.today().year


class ReferenceDict(models.Model):
    """Базовый класс для справочников (словарей)."""

    code = models.CharField(max_length=50, unique=True, verbose_name='Код')
    label = models.CharField(max_length=255, verbose_name='Название')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')

    class Meta:
        abstract = True
        ordering = ['sort_order', 'code']

    def __str__(self):
        return self.label


class PublicationTypeDict(ReferenceDict):
    class Meta:
        verbose_name = 'Тип публикации'
        verbose_name_plural = 'Типы публикаций'


class CitationDatabaseDict(ReferenceDict):
    class Meta:
        verbose_name = 'База цитирования'
        verbose_name_plural = 'Базы цитирования'


class PublicationScopeDict(ReferenceDict):
    class Meta:
        verbose_name = 'Уровень публикации'
        verbose_name_plural = 'Уровни публикаций'


class AuthorStatusDict(ReferenceDict):
    class Meta:
        verbose_name = 'Статус автора'
        verbose_name_plural = 'Статусы авторов'


class ReportingPeriodDict(ReferenceDict):
    class Meta:
        verbose_name = 'Отчётный период'
        verbose_name_plural = 'Отчётные периоды'


class ResultDict(ReferenceDict):
    class Meta:
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'


class Publication(models.Model):
    MONTH_CHOICES = [
        (1, 'Январь'), (2, 'Февраль'), (3, 'Март'), (4, 'Апрель'),
        (5, 'Май'), (6, 'Июнь'), (7, 'Июль'), (8, 'Август'),
        (9, 'Сентябрь'), (10, 'Октябрь'), (11, 'Ноябрь'), (12, 'Декабрь'),
    ]

    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('marked_for_deletion', 'Помечена на удаление'),
        ('archived', 'Архивирована'),
    ]

    MODERATION_STATUS = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    title = models.TextField(verbose_name='Название публикации/мероприятия')
    author = models.TextField(verbose_name='Автор(ы)')

    head = models.CharField(max_length=255, blank=True, verbose_name='Руководитель')
    executors = models.TextField(blank=True, verbose_name='Исполнители')
    location = models.CharField(max_length=255, blank=True, verbose_name='Место проведения')
    event_name = models.CharField(max_length=255, blank=True, verbose_name='Название мероприятия')
    funding_source = models.CharField(max_length=255, blank=True, verbose_name='Источник финансирования')
    volume = models.CharField(max_length=100, blank=True, verbose_name='Объём')
    note = models.TextField(blank=True, verbose_name='Примечание')
    keywords = models.CharField(max_length=255, blank=True, verbose_name='Ключевые слова')
    students_names = models.TextField(blank=True, verbose_name='ФИО студентов')

    year = models.IntegerField(
        verbose_name='Год издания',
        validators=[MinValueValidator(1900), MaxValueValidator(current_year)]
    )
    students_count = models.PositiveIntegerField(default=0, verbose_name='Количество студентов')
    pages_count = models.PositiveIntegerField(default=0, verbose_name='Количество страниц')

    result = models.ForeignKey(
        'ResultDict',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Результат'
    )
    citation_db = models.ForeignKey(
        'CitationDatabaseDict',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='База данных и система цитирования'
    )
    publication_type = models.ForeignKey(
        'PublicationTypeDict',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Тип публикации'
    )
    publication_scope = models.ForeignKey(
        'PublicationScopeDict',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Уровень публикации'
    )
    author_status = models.ForeignKey(
        'AuthorStatusDict',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Статус автора'
    )
    reporting_period = models.ForeignKey(
        'ReportingPeriodDict',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Отчётный период'
    )

    publisher = models.ForeignKey(
        'Publisher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Издательство'
    )
    printed_sheets = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Объём в печатных листах'
    )
    circulation = models.PositiveIntegerField(default=0, verbose_name='Тираж')

    doi = models.CharField(max_length=100, blank=True, verbose_name='DOI')
    edn_code = models.CharField(max_length=20, blank=True, verbose_name='EDN')
    elibrary_id = models.CharField(max_length=50, blank=True, verbose_name='ELibrary ID')

    reporting_year = models.CharField(max_length=10, blank=True, verbose_name='Отчётный год')

    department = models.ForeignKey(
        'users.Department',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Кафедра'
    )
    entry_month = models.IntegerField(choices=MONTH_CHOICES, default=datetime.date.today().month, verbose_name='Месяц внесения')
    event_date = models.DateField(null=True, blank=True, verbose_name='Дата проведения')

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Владелец записи'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Статус записи'
    )
    moderation_status = models.CharField(
        max_length=20,
        choices=MODERATION_STATUS,
        default='pending',
        verbose_name='Статус модерации'
    )
    is_archived = models.BooleanField(default=False, verbose_name='В архиве')
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_publications',
        verbose_name='Кем проверено'
    )
    moderated_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата проверки')
    moderation_comment = models.TextField(blank=True, verbose_name='Комментарий модератора')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['department', 'year']),
            models.Index(fields=['title']),
            models.Index(fields=['publication_type']),
            models.Index(fields=['citation_db']),
            models.Index(fields=['reporting_period']),
            models.Index(fields=['is_archived', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.author})"


class Publisher(models.Model):
    name = models.TextField(unique=True, verbose_name='Название издательства')
    city = models.CharField(max_length=100, blank=True, verbose_name='Город')
    country = models.CharField(max_length=100, blank=True, verbose_name='Страна')
    website = models.URLField(blank=True, verbose_name='Сайт')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Издательство'
        verbose_name_plural = 'Издательства'
        ordering = ['name']

    def __str__(self):
        return self.name


class DeleteRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='delete_requests',
        verbose_name='Публикация'
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='delete_requests',
        verbose_name='Заявитель'
    )
    reason = models.TextField(verbose_name='Причина удаления')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_delete_requests',
        verbose_name='Кем рассмотрено'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата рассмотрения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Запрос на удаление'
        verbose_name_plural = 'Запросы на удаление'
        ordering = ['-created_at']

    def __str__(self):
        return f"Запрос на удаление #{self.id} - {self.publication.title}"


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Создание'),
        ('update', 'Обновление'),
        ('soft_delete', 'Мягкое удаление'),
        ('hard_delete', 'Физическое удаление'),
        ('restore', 'Восстановление'),
        ('delete_request', 'Запрос на удаление'),
        ('delete_request_approved', 'Одобрение запроса'),
        ('delete_request_rejected', 'Отклонение запроса'),
        ('moderation_approved', 'Публикация одобрена'),
        ('moderation_rejected', 'Публикация отклонена'),
        ('login', 'Вход в систему'),
        ('logout', 'Выход из системы'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name='Пользователь'
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES, verbose_name='Действие')
    publication = models.ForeignKey(
        Publication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name='Публикация'
    )
    details = models.JSONField(default=dict, blank=True, verbose_name='Детали')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP-адрес')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время')

    class Meta:
        verbose_name = 'Журнал активности'
        verbose_name_plural = 'Журнал активности'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.user} - {self.timestamp}"