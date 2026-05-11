from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


PRIORITY_CHOICES = [
    ('low', 'Basse'),
    ('medium', 'Moyenne'),
    ('high', 'Haute'),
    ('urgent', 'Urgente'),
]


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name='Nom')
    description = models.TextField(blank=True)
    default_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_ticket_categories',
        limit_choices_to={'role__in': ['admin', 'agent']},
        verbose_name='Agent par defaut',
    )

    class Meta:
        verbose_name = 'Categorie'
        verbose_name_plural = 'Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name


class SLA(models.Model):
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, unique=True)
    response_hours = models.PositiveIntegerField(default=24, verbose_name='Delai de reponse')
    resolution_hours = models.PositiveIntegerField(default=72, verbose_name='Delai de resolution')

    class Meta:
        verbose_name = 'SLA'
        verbose_name_plural = 'SLA'

    def __str__(self):
        return f'{self.get_priority_display()} - {self.resolution_hours}h'


class Ticket(models.Model):
    class Priority(models.TextChoices):
        LOW = PRIORITY_CHOICES[0]
        MEDIUM = PRIORITY_CHOICES[1]
        HIGH = PRIORITY_CHOICES[2]
        URGENT = PRIORITY_CHOICES[3]

    class Status(models.TextChoices):
        NEW = 'new', 'Nouveau'
        ACCEPTED = 'accepted', 'Accepte'
        REFUSED = 'refused', 'Refuse'
        IN_PROGRESS = 'in_progress', 'En cours'
        WAITING = 'waiting', 'En attente'
        RESOLVED = 'resolved', 'Resolu'
        CLOSED = 'closed', 'Ferme'

    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='tickets', verbose_name='Categorie')
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM, verbose_name='Priorite')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name='Statut')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tickets')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        limit_choices_to={'role__in': ['admin', 'agent']},
        verbose_name='Agent assigne',
    )
    estimated_resolution = models.DateTimeField(null=True, blank=True, verbose_name='Resolution estimee')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f'#{self.pk} - {self.title}'

    def get_absolute_url(self):
        return reverse('tickets:detail', args=[self.pk])

    def save(self, *args, **kwargs):
        if self.pk:
            old = Ticket.objects.filter(pk=self.pk).only('status').first()
            if old and old.status != self.status:
                now = timezone.now()
                if self.status == self.Status.RESOLVED and not self.resolved_at:
                    self.resolved_at = now
                if self.status == self.Status.CLOSED and not self.closed_at:
                    self.closed_at = now
        if not self.estimated_resolution:
            try:
                sla = SLA.objects.get(priority=self.priority)
                self.estimated_resolution = timezone.now() + timezone.timedelta(hours=sla.resolution_hours)
            except SLA.DoesNotExist:
                self.estimated_resolution = timezone.now() + timezone.timedelta(hours=72)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.estimated_resolution and self.estimated_resolution < timezone.now() and self.status not in {
            self.Status.RESOLVED,
            self.Status.CLOSED,
        }


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    comment = models.ForeignKey(
        'TicketComment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attachments',
    )
    file = models.FileField(upload_to='tickets/attachments/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    @property
    def is_image(self):
        return self.file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(verbose_name='Message')
    is_internal = models.BooleanField(default=False, verbose_name='Note interne')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'Commentaire de {self.author} sur #{self.ticket_id}'


class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=180)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Historique'
        verbose_name_plural = 'Historiques'

    def __str__(self):
        return self.action
