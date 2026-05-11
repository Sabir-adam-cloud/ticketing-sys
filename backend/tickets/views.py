from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from users.models import CustomUser
from .forms import TicketCommentForm, TicketCreateForm, TicketUpdateForm
from .models import Ticket, TicketAttachment, TicketHistory


def _can_access(user, ticket):
    return user.is_support_agent or ticket.created_by_id == user.id


def _visible_comments(user, ticket):
    comments = ticket.comments.select_related('author').prefetch_related('attachments')
    if not user.is_support_agent:
        comments = comments.filter(is_internal=False)
    return comments


def _can_answer_ticket(user, ticket):
    if not user.is_support_agent:
        return True
    return ticket.status in {
        Ticket.Status.ACCEPTED,
        Ticket.Status.IN_PROGRESS,
        Ticket.Status.WAITING,
    }


def _assign_agent(ticket):
    if ticket.category.default_agent:
        return ticket.category.default_agent
    return (
        CustomUser.objects.filter(role__in=[CustomUser.Role.ADMIN, CustomUser.Role.AGENT])
        .annotate(open_count=Count('assigned_tickets', filter=~Q(assigned_tickets__status__in=[
            Ticket.Status.RESOLVED,
            Ticket.Status.CLOSED,
        ])))
        .order_by('open_count', 'id')
        .first()
    )


def _notify(subject, message, recipients):
    emails = [email for email in recipients if email]
    if emails:
        send_mail(subject, message, None, emails, fail_silently=True)


@login_required
def dashboard(request):
    tickets = Ticket.objects.select_related('category', 'created_by', 'assigned_to')
    if request.user.is_support_admin:
        return redirect('tickets:admin_dashboard')
    if request.user.is_support_agent:
        base_queue = tickets.exclude(status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED, Ticket.Status.REFUSED])
    else:
        base_queue = tickets.filter(created_by=request.user)

    status = request.GET.get('status')
    priority = request.GET.get('priority')
    category = request.GET.get('category')
    overdue = request.GET.get('overdue')
    show_all = request.GET.get('show') == 'all'

    queue = base_queue
    if not request.user.is_support_agent and not status and not show_all:
        queue = queue.exclude(status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED, Ticket.Status.REFUSED])
    if status:
        queue = queue.filter(status=status)
    if priority:
        queue = queue.filter(priority=priority)
    if category:
        queue = queue.filter(category_id=category)
    if overdue:
        queue = [ticket for ticket in queue if ticket.is_overdue]

    stats = {
        'total': base_queue.count(),
        'new': base_queue.filter(status=Ticket.Status.NEW).count(),
        'overdue': sum(1 for ticket in base_queue if ticket.is_overdue),
        'resolved': base_queue.filter(status=Ticket.Status.RESOLVED).count(),
    }
    return render(request, 'tickets/dashboard.html', {
        'tickets': queue,
        'stats': stats,
        'status_choices': Ticket.Status.choices,
        'priority_choices': Ticket.Priority.choices,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_support_admin:
        messages.error(request, 'Acces reserve aux administrateurs.')
        return redirect('tickets:dashboard')

    tickets = Ticket.objects.select_related('category', 'created_by', 'assigned_to')
    selected_agent = request.GET.get('agent')
    selected_status = request.GET.get('status')
    visible_tickets = tickets
    if selected_agent:
        visible_tickets = visible_tickets.filter(assigned_to_id=selected_agent)
    if selected_status:
        visible_tickets = visible_tickets.filter(status=selected_status)

    agents = (
        CustomUser.objects.filter(role=CustomUser.Role.AGENT)
        .annotate(
            total_tickets=Count('assigned_tickets'),
            open_tickets=Count(
                'assigned_tickets',
                filter=~Q(assigned_tickets__status__in=[
                    Ticket.Status.RESOLVED,
                    Ticket.Status.CLOSED,
                    Ticket.Status.REFUSED,
                ]),
            ),
            accepted_tickets=Count('assigned_tickets', filter=Q(assigned_tickets__status=Ticket.Status.ACCEPTED)),
            refused_tickets=Count('assigned_tickets', filter=Q(assigned_tickets__status=Ticket.Status.REFUSED)),
            resolved_tickets=Count('assigned_tickets', filter=Q(assigned_tickets__status=Ticket.Status.RESOLVED)),
        )
        .order_by('username')
    )
    stats = {
        'total': tickets.count(),
        'new': tickets.filter(status=Ticket.Status.NEW).count(),
        'accepted': tickets.filter(status=Ticket.Status.ACCEPTED).count(),
        'waiting': tickets.filter(status=Ticket.Status.WAITING).count(),
        'in_progress': tickets.filter(status=Ticket.Status.IN_PROGRESS).count(),
        'refused': tickets.filter(status=Ticket.Status.REFUSED).count(),
        'resolved': tickets.filter(status=Ticket.Status.RESOLVED).count(),
    }
    return render(request, 'tickets/admin_dashboard.html', {
        'tickets': visible_tickets,
        'agents': agents,
        'stats': stats,
        'selected_agent': selected_agent,
        'selected_status': selected_status,
    })


@login_required
def create_ticket(request):
    if request.user.is_support_agent:
        messages.error(request, 'La creation de ticket est reservee aux clients.')
        return redirect('tickets:dashboard')

    if request.method == 'POST':
        form = TicketCreateForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.assigned_to = _assign_agent(ticket)
            ticket.save()
            if form.cleaned_data.get('attachment'):
                TicketAttachment.objects.create(
                    ticket=ticket,
                    file=form.cleaned_data['attachment'],
                    uploaded_by=request.user,
                )
            TicketHistory.objects.create(ticket=ticket, actor=request.user, action='Ticket cree')
            _notify(
                f'Nouveau ticket #{ticket.pk}',
                f'{ticket.title}\nPriorite: {ticket.get_priority_display()}',
                [ticket.assigned_to.email if ticket.assigned_to else None],
            )
            messages.success(request, 'Ticket cree avec succes.')
            return redirect(ticket)
    else:
        form = TicketCreateForm()
    return render(request, 'tickets/ticket_form.html', {'form': form, 'title': 'Nouveau ticket'})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket.objects.select_related('category', 'created_by', 'assigned_to'), pk=pk)
    if not _can_access(request.user, ticket):
        messages.error(request, 'Acces refuse.')
        return redirect('tickets:dashboard')

    if request.method == 'POST':
        form = TicketCommentForm(request.POST, request.FILES)
        if request.user.is_support_agent and not _can_answer_ticket(request.user, ticket):
            messages.error(request, 'Acceptez le ticket ou mettez-le en traitement avant de repondre.')
            return redirect(ticket)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            if request.user.is_support_agent:
                comment.is_internal = False
            elif comment.is_internal:
                comment.is_internal = False
            comment.save()
            if form.cleaned_data.get('attachment'):
                TicketAttachment.objects.create(
                    ticket=ticket,
                    comment=comment,
                    file=form.cleaned_data['attachment'],
                    uploaded_by=request.user,
                )
            history_action = 'Commentaire ajoute'
            if request.user.is_support_agent:
                ticket.status = Ticket.Status.RESOLVED
                ticket.save()
                history_action = 'Reponse agent ajoutee et ticket archive'
            TicketHistory.objects.create(ticket=ticket, actor=request.user, action=history_action)
            recipients = []
            if request.user != ticket.created_by:
                recipients.append(ticket.created_by.email)
            if ticket.assigned_to and request.user != ticket.assigned_to:
                recipients.append(ticket.assigned_to.email)
            _notify(f'Mise a jour ticket #{ticket.pk}', comment.message, recipients)
            messages.success(request, 'Commentaire ajoute.')
            return redirect(ticket)
    else:
        form = TicketCommentForm()
        if 'is_internal' in form.fields:
            form.fields.pop('is_internal')
        if not _can_answer_ticket(request.user, ticket):
            form = None

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'comments': _visible_comments(request.user, ticket),
        'ticket_attachments': ticket.attachments.filter(comment__isnull=True),
        'history': ticket.history.select_related('actor'),
        'form': form,
        'can_answer': _can_answer_ticket(request.user, ticket),
        'now': timezone.now(),
    })


@login_required
def ticket_decision(request, pk, decision):
    ticket = get_object_or_404(Ticket, pk=pk)
    if not request.user.is_support_agent:
        messages.error(request, 'Seuls les agents peuvent traiter les tickets.')
        return redirect(ticket)
    if request.method != 'POST':
        return redirect(ticket)

    if decision == 'accept':
        ticket.status = Ticket.Status.ACCEPTED
        if not ticket.assigned_to:
            ticket.assigned_to = request.user
        ticket.save()
        TicketHistory.objects.create(ticket=ticket, actor=request.user, action='Ticket accepte')
        _notify(
            f'Ticket #{ticket.pk} accepte',
            f'Votre ticket "{ticket.title}" a ete accepte par le support.',
            [ticket.created_by.email],
        )
        messages.success(request, 'Ticket accepte.')
    elif decision == 'waiting':
        ticket.status = Ticket.Status.WAITING
        if not ticket.assigned_to:
            ticket.assigned_to = request.user
        ticket.save()
        TicketHistory.objects.create(ticket=ticket, actor=request.user, action='Ticket mis en attente')
        _notify(
            f'Ticket #{ticket.pk} mis en attente',
            f'Votre ticket "{ticket.title}" est dans la liste d attente.',
            [ticket.created_by.email],
        )
        messages.success(request, 'Ticket mis en liste d attente.')
    elif decision == 'process':
        ticket.status = Ticket.Status.IN_PROGRESS
        if not ticket.assigned_to:
            ticket.assigned_to = request.user
        ticket.save()
        TicketHistory.objects.create(ticket=ticket, actor=request.user, action='Traitement du ticket demarre')
        messages.success(request, 'Traitement du ticket demarre.')
    elif decision == 'refuse':
        ticket.status = Ticket.Status.REFUSED
        ticket.save()
        TicketHistory.objects.create(ticket=ticket, actor=request.user, action='Ticket refuse')
        _notify(
            f'Ticket #{ticket.pk} refuse',
            f'Votre ticket "{ticket.title}" a ete refuse par le support.',
            [ticket.created_by.email],
        )
        messages.success(request, 'Ticket refuse.')
    return redirect(ticket)


@login_required
def update_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if not request.user.is_support_agent:
        messages.error(request, 'Seuls les agents peuvent modifier le traitement.')
        return redirect(ticket)

    old_status = ticket.status
    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save()
            action = 'Ticket modifie'
            if old_status != ticket.status:
                action = f'Statut: {ticket.get_status_display()}'
            TicketHistory.objects.create(ticket=ticket, actor=request.user, action=action)
            _notify(
                f'Ticket #{ticket.pk} mis a jour',
                f'Statut actuel: {ticket.get_status_display()}',
                [ticket.created_by.email],
            )
            messages.success(request, 'Ticket mis a jour.')
            return redirect(ticket)
    else:
        form = TicketUpdateForm(instance=ticket)
    return render(request, 'tickets/ticket_form.html', {'form': form, 'title': 'Modifier le ticket'})
