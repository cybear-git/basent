# План рефакторинга проекта Science Publications

## 1. Рефакторинг базы данных (PostgreSQL + Django Models)

### 1.1 Выделение справочных таблиц из Publication

#### Новые модели:

**Author (Авторы)**
```python
class Author(models.Model):
    full_name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True)
    orcid = models.CharField(max_length=50, blank=True)
    affiliation = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**DepartmentReference (Справочник кафедр)**
- Заменить строковое поле `department` на ForeignKey
- Использовать существующую модель `Department` из users или создать новую

**CitationDatabase (Базы цитирования)**
```python
class CitationDatabase(models.Model):
    code = models.CharField(max_length=20, unique=True)  # RINC, VAK, WOS, etc.
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
```

**PublicationType (Типы публикаций)**
```python
class PublicationType(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # article, book, conference, etc.
```

**PublicationScope (Уровень публикаций)**
```python
class PublicationScope(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
```

**ResultType (Типы результатов)**
```python
class ResultType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
```

**AuthorStatus (Статус автора)**
```python
class AuthorStatus(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
```

**ReportingPeriod (Отчётные периоды)**
```python
class ReportingPeriod(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    quarter = models.IntegerField(null=True, blank=True)
```

### 1.2 Обновлённая модель Publication

```python
class Publication(models.Model):
    # Основная информация
    title = models.TextField(verbose_name='Название публикации/мероприятия')
    
    # Связи с нормализованными справочниками
    authors = models.ManyToManyField(Author, through='PublicationAuthor')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    citation_db = models.ForeignKey(CitationDatabase, on_delete=models.SET_NULL, null=True)
    publication_type = models.ForeignKey(PublicationType, on_delete=models.SET_NULL, null=True)
    publication_scope = models.ForeignKey(PublicationScope, on_delete=models.SET_NULL, null=True)
    result = models.ForeignKey(ResultType, on_delete=models.SET_NULL, null=True)
    author_status = models.ForeignKey(AuthorStatus, on_delete=models.SET_NULL, null=True)
    reporting_period = models.ForeignKey(ReportingPeriod, on_delete=models.SET_NULL, null=True)
    
    # Оставшиеся поля
    year = models.IntegerField()
    event_date = models.DateField(null=True, blank=True)
    # ... остальные поля
```

### 1.3 Промежуточная модель для авторов

```python
class PublicationAuthor(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)  # Порядок авторства
    is_corresponding = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
```

## 2. Миграция данных

### 2.1 Скрипт миграции данных

```python
# core/management/commands/migrate_to_normalized_db.py
from django.core.management.base import BaseCommand
from core.models import Publication, Author, CitationDatabase, PublicationType, etc.

class Command(BaseCommand):
    def handle(self, *args, **options):
        # 1. Создать справочные записи из существующих данных
        # 2. Обновить Publication с новыми ForeignKey
        # 3. Перенести данные об авторах
```

### 2.2 SQL миграция для PostgreSQL

```sql
-- Создание новых таблиц
-- Перенос данных
-- Обновление внешних ключей
-- Удаление старых колонок
```

## 3. Обновление API (Django REST Framework)

### 3.1 Новые сериализаторы

```python
# core/serializers.py
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'full_name', 'email', 'orcid', 'affiliation']

class PublicationListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.short_name', read_only=True)
    citation_db_name = serializers.CharField(source='citation_db.name', read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)
    
class PublicationCreateSerializer(serializers.ModelSerializer):
    authors = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = Publication
        fields = [..., 'authors']
    
    def create(self, validated_data):
        authors_data = validated_data.pop('authors', [])
        publication = super().create(validated_data)
        for author in authors_data:
            PublicationAuthor.objects.create(
                publication=publication,
                author=author
            )
        return publication
```

### 3.2 Обновление ViewSets

```python
# core/views.py
class PublicationViewSet(viewsets.ModelViewSet):
    queryset = Publication.objects.select_related(
        'department', 'citation_db', 'publication_type'
    ).prefetch_related('authors')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PublicationListSerializer
        elif self.action == 'retrieve':
            return PublicationDetailSerializer
        return PublicationCreateSerializer
```

## 4. Frontend (React) - уже соответствует требованиям

### 4.1 Текущий стек оптимален:
- ✅ React 19
- ✅ TypeScript
- ✅ Vite
- ✅ React Router v7
- ✅ Axios для API

### 4.2 Необходимые изменения на фронтенде:

#### Обновление типов данных

```typescript
// frontend/types/index.ts
export interface Author {
  id: number;
  full_name: string;
  email?: string;
  orcid?: string;
}

export interface Department {
  id: number;
  code: string;
  short_name: string;
  full_name: string;
}

export interface Publication {
  id: number;
  title: string;
  authors: Author[];
  department: Department | null;
  year: number;
  // ...
}
```

#### Обновление форм создания/редактирования

```tsx
// frontend/components/PublicationForm.tsx
import { useState, useEffect } from 'react';
import { api } from '../services/api';

const PublicationForm = () => {
  const [authors, setAuthors] = useState<Author[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  
  useEffect(() => {
    const fetchData = async () => {
      const [authorsRes, departmentsRes] = await Promise.all([
        api.get('/api/authors/'),
        api.get('/api/departments/')
      ]);
      setAuthors(authorsRes.data);
      setDepartments(departmentsRes.data);
    };
    fetchData();
  }, []);
  
  // ... форма с select для авторов и кафедр
};
```

## 5. План выполнения

### Этап 1: Подготовка (1-2 дня)
- [ ] Создать резервную копию БД
- [ ] Настроить PostgreSQL (если ещё не настроен)
- [ ] Создать новые модели в `models.py`

### Этап 2: Миграция БД (2-3 дня)
- [ ] Создать и применить миграции Django
- [ ] Написать скрипт миграции данных
- [ ] Протестировать на тестовой БД
- [ ] Применить к продакшен БД

### Этап 3: Обновление API (2-3 дня)
- [ ] Обновить сериализаторы
- [ ] Обновить viewsets
- [ ] Добавить endpoints для справочников
- [ ] Протестировать API

### Этап 4: Обновление фронтенда (2-3 дня)
- [ ] Обновить TypeScript типы
- [ ] Обновить формы создания/редактирования
- [ ] Обновить отображение списков
- [ ] Протестировать UI

### Этап 5: Тестирование и отладка (2-3 дня)
- [ ] Интеграционное тестирование
- [ ] Исправление ошибок
- [ ] Оптимизация производительности

## 6. Преимущества новой структуры

1. **Нормализация БД:**
   - Устранение дублирования данных
   - Целостность данных через FK
   - Легче поддерживать актуальность справочников

2. **Гибкость:**
   - Легко добавлять новые значения в справочники
   - Возможность расширения атрибутов справочников
   - Мультивыбор авторов

3. **Производительность:**
   - Индексы на внешних ключах
   - Оптимизированные запросы через select_related/prefetch_related

4. **Поддержка:**
   - Понятная структура БД
   - Легче вносить изменения
   - Лучшая документированность через модели
