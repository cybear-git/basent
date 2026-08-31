from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime
from django.conf import settings


def current_year():
    return datetime.date.today().year


# === Справочники для нормализации базы данных ===

class Department(models.Model):
    """Справочник кафедр"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код кафедры')
    full_name = models.TextField(verbose_name='Полное название')
    short_name = models.CharField(max_length=100, blank=True, verbose_name='Краткое название')
    description = models.TextField(blank=True, verbose_name='Описание')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Кафедра'
        verbose_name_plural = 'Кафедры'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.short_name or self.full_name}"


class ResultType(models.Model):
    """Справочник результатов (участник, призёр, победитель)"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код результата', default='participant')
    name = models.CharField(max_length=50, unique=True, verbose_name='Название результата')
    display_name = models.CharField(max_length=50, verbose_name='Отображаемое название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Тип результата'
        verbose_name_plural = 'Типы результатов'
        ordering = ['display_name']

    def __str__(self):
        return self.display_name


class CitationDatabase(models.Model):
    """Справочник баз данных цитирования"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код')
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    website = models.URLField(blank=True, verbose_name='Сайт')

    class Meta:
        verbose_name = 'База данных цитирования'
        verbose_name_plural = 'Базы данных цитирования'
        ordering = ['name']

    def __str__(self):
        return self.name


class PublicationType(models.Model):
    """Справочник типов публикаций"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код типа')
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Тип публикации'
        verbose_name_plural = 'Типы публикаций'
        ordering = ['name']

    def __str__(self):
        return self.name


class PublicationScope(models.Model):
    """Справочник уровней публикаций/мероприятий"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код уровня')
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Уровень публикации'
        verbose_name_plural = 'Уровни публикаций'
        ordering = ['name']

    def __str__(self):
        return self.name


class AuthorStatus(models.Model):
    """Справочник статусов авторов"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код статуса')
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Статус автора'
        verbose_name_plural = 'Статусы авторов'
        ordering = ['name']

    def __str__(self):
        return self.name


class ReportingPeriod(models.Model):
    """Справочник отчётных периодов"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код периода')
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    display_order = models.PositiveIntegerField(default=0, verbose_name='Порядок отображения')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Отчётный период'
        verbose_name_plural = 'Отчётные периоды'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Month(models.Model):
    """Справочник месяцев"""
    number = models.PositiveIntegerField(unique=True, verbose_name='Номер месяца')
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    short_name = models.CharField(max_length=10, blank=True, verbose_name='Краткое название')

    class Meta:
        verbose_name = 'Месяц'
        verbose_name_plural = 'Месяцы'
        ordering = ['number']

    def __str__(self):
        return self.name


class EntryStatus(models.Model):
    """Справочник статусов записей"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код статуса')
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    color = models.CharField(max_length=20, blank=True, verbose_name='Цвет для отображения')

    class Meta:
        verbose_name = 'Статус записи'
        verbose_name_plural = 'Статусы записей'
        ordering = ['name']

    def __str__(self):
        return self.name


class ModerationStatus(models.Model):
    """Справочник статусов модерации"""
    code = models.CharField(max_length=50, unique=True, verbose_name='Код статуса')
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    color = models.CharField(max_length=20, blank=True, verbose_name='Цвет для отображения')

    class Meta:
        verbose_name = 'Статус модерации'
        verbose_name_plural = 'Статусы модерации'
        ordering = ['name']

    def __str__(self):
        return self.name


# === Основная модель публикации ===

class Publication(models.Model):
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

    # Связи со справочниками (вместо CHOICES)
    result = models.ForeignKey(
        ResultType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Результат'
    )
    citation_db = models.ForeignKey(
        CitationDatabase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='База данных и система цитирования'
    )
    publication_type = models.ForeignKey(
        PublicationType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Тип публикации'
    )
    publication_scope = models.ForeignKey(
        PublicationScope,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Уровень публикации'
    )
    author_status = models.ForeignKey(
        AuthorStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Статус автора'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Кафедра'
    )
    entry_month = models.ForeignKey(
        Month,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name='publications',
        verbose_name='Месяц внесения'
    )
    reporting_period = models.ForeignKey(
        ReportingPeriod,
        on_delete=models.SET_NULL,
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
    event_date = models.DateField(null=True, blank=True, verbose_name='Дата проведения')

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_publications',
        verbose_name='Владелец записи'
    )
    # Связи со справочниками статусов (вместо CHOICES)
    status = models.ForeignKey(
        EntryStatus,
        on_delete=models.SET_DEFAULT,
        default=None,  # Будет установлен через save()
        related_name='publications_by_status',
        verbose_name='Статус записи'
    )
    moderation_status_rel = models.ForeignKey(
        ModerationStatus,
        on_delete=models.SET_DEFAULT,
        default=None,  # Будет установлен через save()
        related_name='publications_by_moderation_status',
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
            models.Index(fields=['publication_type', '-created_at']),
            models.Index(fields=['citation_db', '-created_at']),
            models.Index(fields=['reporting_period', '-created_at']),
            models.Index(fields=['is_archived', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.author})"

    def save(self, *args, **kwargs):
        # Устанавливаем значения по умолчанию для статусов при создании
        if not self.status_id:
            try:
                self.status = EntryStatus.objects.get(code='active')
            except EntryStatus.DoesNotExist:
                pass
        if not self.moderation_status_rel_id:
            try:
                self.moderation_status_rel = ModerationStatus.objects.get(code='pending')
            except ModerationStatus.DoesNotExist:
                pass
        super().save(*args, **kwargs)


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
