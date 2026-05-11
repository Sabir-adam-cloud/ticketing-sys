from django.db import migrations


def seed_defaults(apps, schema_editor):
    Category = apps.get_model('tickets', 'Category')
    SLA = apps.get_model('tickets', 'SLA')

    for name, description in [
        ('Technique', 'Problemes techniques et bugs'),
        ('Compte', 'Connexion, profil et acces utilisateur'),
        ('Facturation', 'Questions de paiement ou facture'),
        ('General', 'Demandes generales du service client'),
    ]:
        Category.objects.get_or_create(name=name, defaults={'description': description})

    for priority, response_hours, resolution_hours in [
        ('low', 48, 120),
        ('medium', 24, 72),
        ('high', 8, 24),
        ('urgent', 2, 8),
    ]:
        SLA.objects.get_or_create(
            priority=priority,
            defaults={'response_hours': response_hours, 'resolution_hours': resolution_hours},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_defaults, migrations.RunPython.noop),
    ]
