from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from users.models import Department

User = get_user_model()

TRANSLIT = {
    'А': 'a', 'Б': 'b', 'В': 'v', 'Г': 'g', 'Д': 'd', 'Е': 'e', 'Ё': 'e',
    'Ж': 'zh', 'З': 'z', 'И': 'i', 'Й': 'i', 'К': 'k', 'Л': 'l', 'М': 'm',
    'Н': 'n', 'О': 'o', 'П': 'p', 'Р': 'r', 'С': 's', 'Т': 't', 'У': 'u',
    'Ф': 'f', 'Х': 'h', 'Ц': 'c', 'Ч': 'ch', 'Ш': 'sh', 'Щ': 'sch',
    'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'e', 'Ю': 'yu', 'Я': 'ya',
}


def transliterate(code):
    import re
    result = ''.join(TRANSLIT.get(ch.upper(), ch) for ch in code)
    result = result.lower()
    result = re.sub(r'[^a-z0-9]', '', result)
    return result or 'dept'


class Command(BaseCommand):
    help = 'Создание учётных записей методистов для каждой кафедры'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password', default='methodist123',
            help='Пароль по умолчанию для всех методистов'
        )

    def handle(self, *args, **options):
        password = options['password']
        created = []
        existed = []

        for dept in Department.objects.all().order_by('code'):
            base = transliterate(dept.code)
            username = f'methodist_{base}'
            email = f'{username}@example.com'

            user, was_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': 'Методист',
                    'last_name': dept.full_name,
                    'email': email,
                    'role': 'METHODIST',
                    'department': dept.code,
                    'is_active': True,
                },
            )
            if was_created:
                user.set_password(password)
                user.save()
                created.append((username, dept.code, dept.full_name))
            else:
                user.role = 'METHODIST'
                user.department = dept.code
                user.save(update_fields=['role', 'department'])
                existed.append((username, dept.code))

        self.stdout.write('Созданы методисты:')
        for username, code, full_name in created:
            self.stdout.write(f'  {username}  |  {code}  |  пароль: {password}')

        if existed:
            self.stdout.write('Уже существовали (кафедра обновлена):')
            for username, code in existed:
                self.stdout.write(f'  {username}  |  {code}')

        self.stdout.write(self.style.SUCCESS(
            f'Готово: создано {len(created)}, существовало {len(existed)}'
        ))