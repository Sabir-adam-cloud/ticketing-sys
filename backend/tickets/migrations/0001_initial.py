# Generated for the support ticket system

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True, verbose_name='Nom')),
                ('description', models.TextField(blank=True)),
                ('default_agent', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'agent']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='default_ticket_categories', to=settings.AUTH_USER_MODEL, verbose_name='Agent par defaut')),
            ],
            options={
                'verbose_name': 'Categorie',
                'verbose_name_plural': 'Categories',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='SLA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.CharField(choices=[('low', 'Basse'), ('medium', 'Moyenne'), ('high', 'Haute'), ('urgent', 'Urgente')], max_length=20, unique=True)),
                ('response_hours', models.PositiveIntegerField(default=24, verbose_name='Delai de reponse')),
                ('resolution_hours', models.PositiveIntegerField(default=72, verbose_name='Delai de resolution')),
            ],
            options={
                'verbose_name': 'SLA',
                'verbose_name_plural': 'SLA',
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Titre')),
                ('description', models.TextField(verbose_name='Description')),
                ('priority', models.CharField(choices=[('low', 'Basse'), ('medium', 'Moyenne'), ('high', 'Haute'), ('urgent', 'Urgente')], default='medium', max_length=20, verbose_name='Priorite')),
                ('status', models.CharField(choices=[('new', 'Nouveau'), ('in_progress', 'En cours'), ('waiting', 'En attente'), ('resolved', 'Resolu'), ('closed', 'Ferme')], default='new', max_length=20, verbose_name='Statut')),
                ('estimated_resolution', models.DateTimeField(blank=True, null=True, verbose_name='Resolution estimee')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('assigned_to', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'agent']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tickets', to=settings.AUTH_USER_MODEL, verbose_name='Agent assigne')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tickets', to='tickets.category', verbose_name='Categorie')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_tickets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='TicketAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='tickets/attachments/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='tickets.ticket')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TicketComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='Message')),
                ('is_internal', models.BooleanField(default=False, verbose_name='Note interne')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tickets.ticket')),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='TicketHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=180)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='tickets.ticket')),
            ],
            options={
                'verbose_name': 'Historique',
                'verbose_name_plural': 'Historiques',
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['status', 'priority'], name='tickets_tic_status_b256f6_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['assigned_to', 'status'], name='tickets_tic_assigne_e36302_idx'),
        ),
    ]
