from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import (
    Publication, DeleteRequest, Department, ResultType, CitationDatabase,
    PublicationType, PublicationScope, AuthorStatus, ReportingPeriod, Month,
    EntryStatus, ModerationStatus, Publisher
)
import random
from datetime import datetime, timedelta

User = get_user_model()

TITLES = [
    'Инновационные подходы к таможенному регулированию',
    'Электронная коммерция и таможенные процедуры',
    'Анализ рисков в таможенном контроле',
    'Таможенная экспертиза товаров',
    'Международная торговля и таможенная политика',
    'Цифровизация таможенных процессов',
    'Таможенное администрирование в ЕАЭС',
    'Контроль качества таможенных услуг',
    'Таможенная логистика и цепочки поставок',
    'Правовые аспекты таможенного дела',
]

AUTHORS = [
    'Иванов А.С.', 'Петрова Е.М.', 'Сидоров В.К.', 'Козлова Н.П.',
    'Смирнов Д.Л.', 'Кузнецова О.И.', 'Васильев А.Н.', 'Попова М.С.',
    'Соколов И.Т.', 'Лебедева Р.Д.', 'Новиков П.К.', 'Морозова А.В.',
]

EVENTS = [
    'Международная конференция',
    'Всероссийский форум',
    'Научный семинар',
    'Олимпиада студентов',
    'Конкурс научных работ',
]


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными и справочниками'

    def create_or_get_object(self, model, code_field='code', **kwargs):
        """Создать или получить объект из справочника"""
        obj, created = model.objects.get_or_create(
            defaults={k: v for k, v in kwargs.items() if k != code_field},
            **{code_field: kwargs[code_field]}
        )
        return obj, created

    def handle(self, *args, **options):
        self.stdout.write('=== Заполнение справочников ===')
        
        # Кафедры
        departments_data = [
            {'code': 'КТОиТК', 'full_name': 'Кафедра таможенных операций и таможенного контроля', 'short_name': 'КТОиТК'},
            {'code': 'КТиТЭ', 'full_name': 'Кафедра товароведения и таможенной экспертизы', 'short_name': 'КТиТЭ'},
            {'code': 'КУиЭТД', 'full_name': 'Кафедра управления и экономики таможенного дела', 'short_name': 'КУиЭТД'},
            {'code': 'КЭТиМЭО', 'full_name': 'Кафедра экономической теории и международных экономических отношений', 'short_name': 'КЭТиМЭО'},
            {'code': 'КГПД', 'full_name': 'Кафедра государственно-правовых дисциплин', 'short_name': 'КГПД'},
            {'code': 'КГрПД', 'full_name': 'Кафедра гражданско-правовых дисциплин', 'short_name': 'КГрПД'},
            {'code': 'КУПД', 'full_name': 'Кафедра уголовно-правовых дисциплин', 'short_name': 'КУПД'},
            {'code': 'КГД', 'full_name': 'Кафедра гуманитарных дисциплин', 'short_name': 'КГД'},
            {'code': 'КИЯ', 'full_name': 'Кафедра иностранных языков', 'short_name': 'КИЯ'},
            {'code': 'КИиИТТ', 'full_name': 'Кафедра информатики и информационных таможенных технологий', 'short_name': 'КИиИТТ'},
            {'code': 'КФП', 'full_name': 'Кафедра физической подготовки', 'short_name': 'КФП'},
        ]
        departments = {}
        for dept_data in departments_data:
            dept, created = self.create_or_get_object(Department, code_field='code', **dept_data)
            departments[dept.code] = dept
            if created:
                self.stdout.write(f'  Создана кафедра: {dept.code}')
        
        # Типы результатов
        results_data = [
            {'code': 'participant', 'name': 'Участник', 'display_name': 'Участник'},
            {'code': 'prize_winner', 'name': 'Призёр', 'display_name': 'Призёр'},
            {'code': 'winner', 'name': 'Победитель', 'display_name': 'Победитель'},
        ]
        result_types = {}
        for res_data in results_data:
            res, created = self.create_or_get_object(ResultType, code_field='code', **res_data)
            result_types[res.code] = res
            if created:
                self.stdout.write(f'  Создан тип результата: {res.display_name}')
        
        # Базы цитирования
        citation_dbs_data = [
            {'code': 'VAK', 'name': 'ВАК', 'description': 'Высшая аттестационная комиссия'},
            {'code': 'SCOPUS', 'name': 'Scopus', 'description': 'Международная база цитирования'},
            {'code': 'WOS', 'name': 'Web of Science', 'description': 'Международная база цитирования'},
            {'code': 'RINC', 'name': 'РИНЦ', 'description': 'Российский индекс научного цитирования'},
            {'code': 'OTHER', 'name': 'Прочие издания', 'description': 'Другие публикации'},
        ]
        citation_dbs = {}
        for db_data in citation_dbs_data:
            db, created = self.create_or_get_object(CitationDatabase, code_field='code', **db_data)
            citation_dbs[db.code] = db
            if created:
                self.stdout.write(f'  Создана база цитирования: {db.name}')
        
        # Типы публикаций
        pub_types_data = [
            {'code': 'article', 'name': 'Статья'},
            {'code': 'monograph', 'name': 'Монография'},
            {'code': 'textbook', 'name': 'Учебник'},
            {'code': 'manual', 'name': 'Учебное пособие'},
            {'code': 'thesis', 'name': 'Тезисы'},
            {'code': 'student_article', 'name': 'Студенческая статья'},
        ]
        publication_types = {}
        for pt_data in pub_types_data:
            pt, created = self.create_or_get_object(PublicationType, code_field='code', **pt_data)
            publication_types[pt.code] = pt
            if created:
                self.stdout.write(f'  Создан тип публикации: {pt.name}')
        
        # Уровни публикаций
        pub_scopes_data = [
            {'code': 'international', 'name': 'Международный'},
            {'code': 'national', 'name': 'Всероссийский'},
            {'code': 'regional', 'name': 'Региональный'},
            {'code': 'university', 'name': 'Вузовский'},
        ]
        publication_scopes = {}
        for ps_data in pub_scopes_data:
            ps, created = self.create_or_get_object(PublicationScope, code_field='code', **ps_data)
            publication_scopes[ps.code] = ps
            if created:
                self.stdout.write(f'  Создан уровень публикации: {ps.name}')
        
        # Статусы авторов
        author_statuses_data = [
            {'code': 'teacher', 'name': 'Преподаватель'},
            {'code': 'student', 'name': 'Студент'},
            {'code': 'graduate', 'name': 'Аспирант'},
            {'code': 'external', 'name': 'Внешний автор'},
        ]
        author_statuses = {}
        for as_data in author_statuses_data:
            aus, created = self.create_or_get_object(AuthorStatus, code_field='code', **as_data)
            author_statuses[aus.code] = aus
            if created:
                self.stdout.write(f'  Создан статус автора: {aus.name}')
        
        # Отчётные периоды
        reporting_periods_data = [
            {'code': 'quarter_1', 'name': '1 квартал', 'display_order': 1},
            {'code': 'quarter_2', 'name': '2 квартал', 'display_order': 2},
            {'code': 'quarter_3', 'name': '3 квартал', 'display_order': 3},
            {'code': 'quarter_4', 'name': '4 квартал', 'display_order': 4},
            {'code': 'year', 'name': 'Год', 'display_order': 5},
        ]
        reporting_periods = {}
        for rp_data in reporting_periods_data:
            rp, created = self.create_or_get_object(ReportingPeriod, code_field='code', **rp_data)
            reporting_periods[rp.code] = rp
            if created:
                self.stdout.write(f'  Создан отчётный период: {rp.name}')
        
        # Месяцы
        months_data = [
            {'number': 1, 'name': 'Январь', 'short_name': 'Янв'},
            {'number': 2, 'name': 'Февраль', 'short_name': 'Фев'},
            {'number': 3, 'name': 'Март', 'short_name': 'Мар'},
            {'number': 4, 'name': 'Апрель', 'short_name': 'Апр'},
            {'number': 5, 'name': 'Май', 'short_name': 'Май'},
            {'number': 6, 'name': 'Июнь', 'short_name': 'Июн'},
            {'number': 7, 'name': 'Июль', 'short_name': 'Июл'},
            {'number': 8, 'name': 'Август', 'short_name': 'Авг'},
            {'number': 9, 'name': 'Сентябрь', 'short_name': 'Сен'},
            {'number': 10, 'name': 'Октябрь', 'short_name': 'Окт'},
            {'number': 11, 'name': 'Ноябрь', 'short_name': 'Ноя'},
            {'number': 12, 'name': 'Декабрь', 'short_name': 'Дек'},
        ]
        months = {}
        for m_data in months_data:
            m, created = self.create_or_get_object(Month, code_field='number', **m_data)
            months[m.number] = m
            if created:
                self.stdout.write(f'  Создан месяц: {m.name}')
        
        # Статусы записей
        entry_statuses_data = [
            {'code': 'active', 'name': 'Активная', 'color': '#22c55e'},
            {'code': 'draft', 'name': 'Черновик', 'color': '#f59e0b'},
            {'code': 'archived', 'name': 'Архивирована', 'color': '#6b7280'},
        ]
        entry_statuses = {}
        for es_data in entry_statuses_data:
            es, created = self.create_or_get_object(EntryStatus, code_field='code', **es_data)
            entry_statuses[es.code] = es
            if created:
                self.stdout.write(f'  Создан статус записи: {es.name}')
        
        # Статусы модерации
        moderation_statuses_data = [
            {'code': 'pending', 'name': 'На модерации', 'color': '#f59e0b'},
            {'code': 'approved', 'name': 'Одобрено', 'color': '#22c55e'},
            {'code': 'rejected', 'name': 'Отклонено', 'color': '#ef4444'},
        ]
        moderation_statuses = {}
        for ms_data in moderation_statuses_data:
            ms, created = self.create_or_get_object(ModerationStatus, code_field='code', **ms_data)
            moderation_statuses[ms.code] = ms
            if created:
                self.stdout.write(f'  Создан статус модерации: {ms.name}')
        
        # Издательства
        publishers_data = [
            {'name': 'Издательство "Наука"', 'city': 'Москва', 'country': 'Россия'},
            {'name': 'Издательский дом "Питер"', 'city': 'Санкт-Петербург', 'country': 'Россия'},
            {'name': 'Издательство "Юрайт"', 'city': 'Москва', 'country': 'Россия'},
        ]
        publishers = {}
        for pub_data in publishers_data:
            pub, created = self.create_or_get_object(Publisher, code_field='name', **pub_data)
            publishers[pub.name] = pub
            if created:
                self.stdout.write(f'  Создано издательство: {pub.name}')
        
        self.stdout.write(self.style.SUCCESS('=== Справочники заполнены ==='))
        
        self.stdout.write('Создание пользователей...')
        
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Администратор',
                'last_name': 'Системы',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Создан администратор: admin / admin123'))

        methodist, created = User.objects.get_or_create(
            username='methodist',
            defaults={
                'email': 'methodist@example.com',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'role': 'METHODIST',
                'department': departments.get('КТОиТК'),
            }
        )
        if created:
            methodist.set_password('methodist123')
            methodist.save()
            self.stdout.write(self.style.SUCCESS(f'Создан методист: methodist / methodist123'))

        methodist2, created = User.objects.get_or_create(
            username='methodist2',
            defaults={
                'email': 'methodist2@example.com',
                'first_name': 'Мария',
                'last_name': 'Сидорова',
                'role': 'METHODIST',
                'department': departments.get('КТиТЭ'),
            }
        )
        if created:
            methodist2.set_password('methodist2123')
            methodist2.save()
            self.stdout.write(self.style.SUCCESS(f'Создан методист: methodist2 / methodist2123'))

        self.stdout.write('Создание публикаций...')
        
        publications = []
        for i in range(30):
            owner = random.choice([methodist, methodist2, None])
            dept_list = list(departments.values())
            result_list = list(result_types.values())
            citation_db_list = list(citation_dbs.values())
            pub_type_list = list(publication_types.values())
            pub_scope_list = list(publication_scopes.values())
            author_status_list = list(author_statuses.values())
            month_list = list(months.values())
            entry_status_list = list(entry_statuses.values())
            moderation_status_list = list(moderation_statuses.values())
            
            pub = Publication(
                title=f"{random.choice(TITLES)} #{i+1}",
                author=random.choice(AUTHORS),
                year=random.randint(2020, 2025),
                department=random.choice(dept_list) if dept_list else None,
                result=random.choice(result_list) if random.random() > 0.3 and result_list else None,
                citation_db=random.choice(citation_db_list) if citation_db_list else None,
                publication_type=random.choice(pub_type_list) if pub_type_list else None,
                publication_scope=random.choice(pub_scope_list) if pub_scope_list else None,
                author_status=random.choice(author_status_list) if author_status_list else None,
                circulation=random.randint(100, 1000) if random.random() > 0.5 else 0,
                location='Москва' if random.random() > 0.5 else 'Санкт-Петербург',
                event_name=random.choice(EVENTS) if random.random() > 0.5 else '',
                volume=f"{random.randint(1, 20)} п.л.",
                note='Тестовая публикация' if random.random() > 0.7 else '',
                students_count=random.randint(0, 5),
                pages_count=random.randint(5, 50),
                entry_month=random.choice(month_list) if month_list else None,
                event_date=datetime.now().date() - timedelta(days=random.randint(1, 365)),
                owner=owner,
                status=random.choice(entry_status_list) if entry_status_list else None,
                moderation_status_rel=random.choice(moderation_status_list) if moderation_status_list else None,
            )
            publications.append(pub)
        
        Publication.objects.bulk_create(publications)
        self.stdout.write(self.style.SUCCESS(f'Создано {len(publications)} публикаций'))

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))
