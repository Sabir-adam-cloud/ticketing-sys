from django.contrib.auth.hashers import make_password
from django.db import migrations


def seed_support_accounts(apps, schema_editor):
    CustomUser = apps.get_model('users', 'CustomUser')
    accounts = [
        {
            'username': 'walid',
            'password': 'walid1234',
            'first_name': 'Walid',
            'role': 'agent',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'amine',
            'password': 'amine12345',
            'first_name': 'Amine',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': False,
        },
    ]
    for account in accounts:
        password = account.pop('password')
        user, created = CustomUser.objects.get_or_create(
            username=account['username'],
            defaults={**account, 'password': make_password(password)},
        )
        if not created:
            for field, value in account.items():
                setattr(user, field, value)
            user.password = make_password(password)
            user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_customuser_role'),
    ]

    operations = [
        migrations.RunPython(seed_support_accounts, migrations.RunPython.noop),
    ]
