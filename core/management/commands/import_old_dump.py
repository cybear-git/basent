import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.timezone import get_current_timezone

from users.models import User, Department
from core.models import (
    Publication, ActivityLog,
    PublicationTypeDict, CitationDatabaseDict, PublicationScopeDict,
    AuthorStatusDict, ReportingPeriodDict, ResultDict,
)

RESULT_MAP = {
    'победитель': 'winner',
    'призёр': 'prize_winner',
    'призер': 'prize_winner',
    'участник': 'participant',
}

DEFAULT_PASSWORDS = {
    'admin': 'admin123',
    'methodist': 'methodist123',
    'nio_staff': 'nio123',
}

USER_FIELDS = [
    'id', 'password', 'last_login', 'is_superuser', 'username',
    'first_name', 'last_name', 'email', 'is_staff', 'is_active',
    'date_joined', 'phone', 'department', 'role',
]

PUB_FIELDS = [
    'id', 'title', 'author', 'circulation', 'head', 'executors', 'location',
    'event_name', 'funding_source', 'volume', 'note', 'students_names', 'year',
    'students_count', 'pages_count', 'result', 'department', 'event_date',
    'created_at', 'updated_at', 'status', 'owner_id', 'keywords', 'moderated_at',
    'moderated_by_id', 'moderation_comment', 'moderation_status', 'citation_db',
    'author_status', 'doi', 'edn_code', 'elibrary_id', 'printed_sheets',
    'publication_scope', 'publication_type', 'reporting_period',
    'reporting_year', 'publisher_id', 'is_archived', 'entry_month',
]

LOG_FIELDS = ['id', 'action', 'details', 'ip_address', 'timestamp', 'user_id', 'publication_id']


def find_statement_end(s, start):
    depth = 0
    in_str = False
    i = start
    n = len(s)
    while i < n:
        ch = s[i]
        if in_str:
            if ch == "'":
                if i + 1 < n and s[i + 1] == "'":
                    i += 2
                    continue
                in_str = False
            i += 1
            continue
        if ch == "'":
            in_str = True
            i += 1
            continue
        if ch == '(':
            depth += 1
            i += 1
            continue
        if ch == ')':
            depth -= 1
            i += 1
            continue
        if ch == ';' and depth == 0:
            return i
        i += 1
    return -1


def find_table(text, table):
    key = 'INSERT INTO ' + table
    pos = text.find(key)
    if pos == -1:
        return None
    vals_pos = text.find('VALUES', pos)
    if vals_pos == -1:
        return None
    end = find_statement_end(text, vals_pos)
    return text[vals_pos:end + 1]


def tokenize_values(block):
    tuples = []
    buf = None
    depth = 0
    in_str = False
    i = 0
    n = len(block)
    while i < n:
        ch = block[i]
        if in_str:
            if ch == "'" and i + 1 < n and block[i + 1] == "'":
                if buf is not None:
                    buf.append(ch)
                    buf.append(block[i + 1])
                i += 2
                continue
            if ch == "'":
                in_str = False
            if buf is not None:
                buf.append(ch)
            i += 1
            continue
        if ch == "'":
            in_str = True
            if buf is not None:
                buf.append(ch)
            i += 1
            continue
        if ch == '(':
            if depth == 0:
                buf = ['(']
                depth = 1
            else:
                depth += 1
                if buf is not None:
                    buf.append(ch)
            i += 1
            continue
        if ch == ')':
            depth -= 1
            if buf is not None:
                buf.append(ch)
            if depth == 0:
                tuples.append(''.join(buf))
                buf = None
            i += 1
            continue
        if ch == ';' and depth == 0:
            break
        if buf is not None and depth > 0:
            buf.append(ch)
        i += 1
    return tuples


def split_row(row):
    vals = []
    buf = []
    in_str = False
    i = 0
    s = row[1:-1]
    n = len(s)
    while i < n:
        ch = s[i]
        if in_str:
            buf.append(ch)
            if ch == "'" and i + 1 < n and s[i + 1] == "'":
                buf.append(s[i + 1])
                i += 2
                continue
            if ch == "'":
                in_str = False
            i += 1
            continue
        if ch == "'":
            in_str = True
            buf.append(ch)
            i += 1
            continue
        if ch == ',':
            vals.append(''.join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    vals.append(''.join(buf).strip())
    return vals


def parse_table(text, table):
    rows = []
    search_from = 0
    key = 'INSERT INTO ' + table
    while True:
        pos = text.find(key, search_from)
        if pos == -1:
            break
        vals_pos = text.find('VALUES', pos)
        if vals_pos == -1:
            break
        end = find_statement_end(text, vals_pos)
        block = text[vals_pos:end + 1]
        for t in tokenize_values(block):
            rows.append(split_row(t))
        search_from = end + 1
    return rows


def clean(v):
    v = v.strip()
    if v == 'NULL':
        return None
    if v.startswith("'") and v.endswith("'"):
        return v[1:-1].replace("''", "'")
    return v


def parse_bool(v):
    if v is None:
        return False
    return str(v).strip().lower() in ('true', 't', '1')


def parse_dt(v):
    if not v:
        return None
    for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S'):
        try:
            dt = datetime.strptime(str(v).strip(), fmt)
            return timezone.make_aware(dt, timezone.get_current_timezone())
        except ValueError:
            continue
    return None


def parse_int(v, default=0):
    if v is None or v == '':
        return default
    try:
        return int(float(str(v)))
    except (TypeError, ValueError):
        return default


class Command(BaseCommand):
    help = 'Импорт данных из дампа старой схемы (import_data.sql) в новую нормализованную схему'

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='?', default='import_data.sql')
        parser.add_argument(
            '--keep-passwords',
            action='store_true',
            help='Не менять пароли импортируемых учёток (оставить хэши из дампа)',
        )

    def handle(self, *args, **options):
        path = options['path']
        keep_passwords = options['keep_passwords']

        try:
            text = open(path, 'r', encoding='utf-8').read()
        except FileNotFoundError:
            raise CommandError(f'Файл не найден: {path}')

        now_year = datetime.now().year
        bad_years = 0

        pubtypes = {o.code: o for o in PublicationTypeDict.objects.all()}
        citdbs = {o.code: o for o in CitationDatabaseDict.objects.all()}
        scopes = {o.code: o for o in PublicationScopeDict.objects.all()}
        statuses = {o.code: o for o in AuthorStatusDict.objects.all()}
        periods = {o.code: o for o in ReportingPeriodDict.objects.all()}
        results = {o.code: o for o in ResultDict.objects.all()}
        departments = {o.code: o for o in Department.objects.all()}

        with transaction.atomic():
            users = []
            for row in parse_table(text, 'users_user'):
                if len(row) != len(USER_FIELDS):
                    self.stderr.write(self.style.WARNING(f'Пропушен user-кортеж (полей {len(row)})'))
                    continue
                vals = [clean(v) for v in row]
                d = dict(zip(USER_FIELDS, vals))
                uid = parse_int(d['id'])
                if uid <= 0:
                    continue
                user = User(
                    id=uid,
                    username=d['username'],
                    first_name=d['first_name'] or '',
                    last_name=d['last_name'] or '',
                    email=d['email'] or '',
                    is_staff=parse_bool(d['is_staff']),
                    is_superuser=parse_bool(d['is_superuser']),
                    is_active=parse_bool(d['is_active']),
                    phone=d['phone'] or '',
                    department=d['department'] or '',
                    role=d['role'] or 'NIO_STAFF',
                    date_joined=parse_dt(d['date_joined']) or datetime.now(),
                    last_login=parse_dt(d['last_login']),
                    password=d['password'],
                )
                if not keep_passwords:
                    user.set_password(DEFAULT_PASSWORDS.get(user.username, 'NioPass123!'))
                users.append(user)
            User.objects.bulk_create(users)
            self.stdout.write(self.style.SUCCESS(f'Импортировано пользователей: {len(users)}'))
            if not keep_passwords:
                self.stdout.write('Пароли установлены на тестовые: admin/admin123, methodist/methodist123, nio_staff/nio123')

            user_ids = {u.username: u.id for u in users}

            pubs = []
            missing_refs = set()
            for row in parse_table(text, 'core_publication'):
                if len(row) != len(PUB_FIELDS):
                    self.stderr.write(self.style.WARNING(f'Пропущена публикация (полей {len(row)})'))
                    continue
                vals = [clean(v) for v in row]
                d = dict(zip(PUB_FIELDS, vals))

                pub_id = parse_int(d['id'])
                if pub_id <= 0:
                    continue

                year = parse_int(d['year'], 2000)
                if not (1900 <= year <= now_year):
                    bad_years += 1
                    year = 2000

                result = None
                if d['result']:
                    code = RESULT_MAP.get(d['result'].strip().lower(), None)
                    result = results.get(code) if code else None

                pubtype = pubtypes.get(d['publication_type']) if d['publication_type'] else None
                citdb = citdbs.get(d['citation_db']) if d['citation_db'] else None
                scope = scopes.get(d['publication_scope']) if d['publication_scope'] else None
                astatus = statuses.get(d['author_status']) if d['author_status'] else None
                period = periods.get(d['reporting_period']) if d['reporting_period'] else None
                dept = departments.get(d['department']) if d['department'] else None

                if d['department'] and not dept:
                    missing_refs.add(f'department={d["department"]}')

                try:
                    printed_sheets = Decimal(str(d['printed_sheets'] or 0))
                except (InvalidOperation, ValueError):
                    printed_sheets = Decimal('0')

                owner_id = parse_int(d['owner_id'], None)
                moderator_id = parse_int(d['moderated_by_id'], None)

                pubs.append(Publication(
                    id=pub_id,
                    title=d['title'],
                    author=d['author'] or 'Неизвестный',
                    head=d['head'] or '',
                    executors=d['executors'] or '',
                    location=d['location'] or '',
                    event_name=d['event_name'] or '',
                    funding_source=d['funding_source'] or '',
                    volume=d['volume'] or '',
                    note=d['note'] or '',
                    keywords=d['keywords'] or '',
                    students_names=d['students_names'] or '',
                    year=year,
                    students_count=parse_int(d['students_count']),
                    pages_count=parse_int(d['pages_count']),
                    result=result,
                    citation_db=citdb,
                    publication_type=pubtype,
                    publication_scope=scope,
                    author_status=astatus,
                    reporting_period=period,
                    publisher=None,
                    printed_sheets=printed_sheets,
                    circulation=parse_int(d['circulation']),
                    doi=d['doi'] or '',
                    edn_code=d['edn_code'] or '',
                    elibrary_id=d['elibrary_id'] or '',
                    reporting_year=d['reporting_year'] or '',
                    department=dept,
                    entry_month=parse_int(d['entry_month'], 5),
                    event_date=None,
                    created_at=parse_dt(d['created_at']),
                    updated_at=parse_dt(d['updated_at']),
                    owner=User(id=owner_id) if owner_id else None,
                    status=d['status'] or 'active',
                    moderation_status=d['moderation_status'] or 'pending',
                    moderation_comment=d['moderation_comment'] or '',
                    is_archived=parse_bool(d['is_archived']),
                    moderated_by=User(id=moderator_id) if moderator_id else None,
                    moderated_at=parse_dt(d['moderated_at']),
                ))
            Publication.objects.bulk_create(pubs)
            self.stdout.write(self.style.SUCCESS(f'Импортировано публикаций: {len(pubs)}'))
            if bad_years:
                self.stdout.write(self.style.WARNING(f'Некорректный год исправлен на 2000 в {bad_years} записи(ях)'))
            for ref in missing_refs:
                self.stdout.write(self.style.WARNING(f'Не найдена ссылка: {ref}'))

            logs = 0
            skipped_logs = 0
            for row in parse_table(text, 'core_activitylog'):
                if len(row) != len(LOG_FIELDS):
                    continue
                vals = [clean(v) for v in row]
                d = dict(zip(LOG_FIELDS, vals))
                details = {}
                if d['details']:
                    try:
                        details = json.loads(d['details'])
                    except (ValueError, TypeError):
                        details = {'raw': d['details']}
                ActivityLog.objects.create(
                    id=parse_int(d['id']),
                    action=d['action'],
                    details=details,
                    ip_address=d['ip_address'] or None,
                    timestamp=parse_dt(d['timestamp']) or datetime.now(),
                    user_id=parse_int(d['user_id'], None),
                    publication_id=parse_int(d['publication_id'], None),
                )
                logs += 1
            self.stdout.write(self.style.SUCCESS(f'Импортировано записей журнала: {logs}'))

        self.stdout.write(self.style.SUCCESS('Импорт успешно завершён.'))