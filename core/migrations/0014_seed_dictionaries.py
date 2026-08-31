from django.db import migrations


def seed_dictionaries(apps, schema_editor):
    PublicationTypeDict = apps.get_model('core', 'PublicationTypeDict')
    CitationDatabaseDict = apps.get_model('core', 'CitationDatabaseDict')
    PublicationScopeDict = apps.get_model('core', 'PublicationScopeDict')
    AuthorStatusDict = apps.get_model('core', 'AuthorStatusDict')
    ReportingPeriodDict = apps.get_model('core', 'ReportingPeriodDict')
    ResultDict = apps.get_model('core', 'ResultDict')

    def _seed(model, values):
        for order, (code, label) in enumerate(values):
            model.objects.get_or_create(
                code=code,
                defaults={'label': label, 'sort_order': order},
            )

    _seed(PublicationTypeDict, [
        ('article', 'Статья',),
        ('student_article', 'Статья студента',),
        ('monograph', 'Монография',),
        ('textbook', 'Учебник',),
        ('tutorial', 'Учебное пособие',),
        ('conference_paper', 'Тезисы докладов',),
        ('software_certificate', 'Свидетельство ЭВМ',),
        ('patent', 'Патенты на изобретения',),
        ('student_research', 'НИРС',),
        ('conference', 'Научная конференция',),
        ('forum', 'Научный форум',),
        ('competition', 'Научный конкурс',),
        ('exhibition', 'Выставка',),
        ('round_table', 'Круглый стол',),
        ('conference_collection', 'Сборник трудов конференции',),
    ])

    _seed(CitationDatabaseDict, [
        ('RINC', 'РИНЦ',),
        ('VAK', 'ВАК',),
        ('WOS', 'WOS',),
        ('SCOPUS', 'Scopus',),
        ('OTHER_DB', 'Другие издания',),
        ('NONE', 'Без индексации',),
    ])

    _seed(PublicationScopeDict, [
        ('international', 'Международное',),
        ('all_russian', 'Всероссийское',),
        ('regional', 'Региональное',),
        ('interuniversity', 'Межвузовское',),
        ('internal', 'Внутривузовское',),
    ])

    _seed(AuthorStatusDict, [
        ('staff', 'Штатный сотрудник',),
        ('student', 'Студент',),
        ('compatibility', 'Совместитель',),
        ('external', 'Внешний сотрудник',),
    ])

    _seed(ReportingPeriodDict, [
        ('1_quarter', '1 квартал',),
        ('2_quarter', '2 квартал',),
        ('3_quarter', '3 квартал',),
        ('4_quarter', '4 квартал',),
        ('1_period', '1 период',),
        ('2_period', '2 период',),
        ('3_period', '3 период',),
        ('4_period', '4 период',),
        ('annual', 'Годовой отчёт',),
    ])

    _seed(ResultDict, [
        ('participant', 'Участник',),
        ('prize_winner', 'Призёр',),
        ('winner', 'Победитель',),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_authorstatusdict_citationdatabasedict_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_dictionaries, migrations.RunPython.noop),
    ]