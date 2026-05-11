# Generated for support ticket roles

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin', 'Administrateur'),
                    ('agent', 'Agent de support'),
                    ('client', 'Client'),
                ],
                default='client',
                max_length=20,
                verbose_name='Role',
            ),
        ),
    ]
