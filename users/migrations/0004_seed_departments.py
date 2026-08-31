from django.db import migrations


def seed_departments(apps, schema_editor):
    Department = apps.get_model('users', 'Department')
    departments = [
        ('КТОиТК', 'Кафедра таможенных операций и таможенного контроля', 'КТОиТК'),
        ('КТиТЭ', 'Кафедра товароведения и таможенной экспертизы', 'КТиТЭ'),
        ('КУиЭТД', 'Кафедра управления и экономики таможенного дела', 'КУиЭТД'),
        ('КЭТиМЭО', 'Кафедра экономической теории и международных экономических отношений', 'КЭТиМЭО'),
        ('КГПД', 'Кафедра государственно-правовых дисциплин', 'КГПД'),
        ('КГрПД', 'Кафедра гражданско-правовых дисциплин', 'КГрПД'),
        ('КУПД', 'Кафедра уголовно-правовых дисциплин', 'КУПД'),
        ('КГД', 'Кафедра гуманитарных дисциплин', 'КГД'),
        ('КИЯ', 'Кафедра иностранных языков', 'КИЯ'),
        ('КИиИТТ', 'Кафедра информатики и информационных таможенных технологий', 'КИиИТТ'),
        ('КФП', 'Кафедра физической подготовки', 'КФП'),
    ]
    for code, full_name, short_name in departments:
        Department.objects.get_or_create(
            code=code,
            defaults={'full_name': full_name, 'short_name': short_name},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_add_nio_staff_role'),
    ]

    operations = [
        migrations.RunPython(seed_departments, migrations.RunPython.noop),
    ]