from django import forms

from users.models import CustomUser
from .models import Ticket, TicketAttachment, TicketComment


def _bootstrap_fields(form):
    for field in form.fields.values():
        css_class = 'form-check-input' if isinstance(field.widget, forms.CheckboxInput) else 'form-control'
        if isinstance(field.widget, forms.Select):
            css_class = 'form-select'
        field.widget.attrs['class'] = css_class


class TicketCreateForm(forms.ModelForm):
    attachment = forms.FileField(required=False, label='Piece jointe')

    class Meta:
        model = Ticket
        fields = ('title', 'description', 'category', 'priority', 'attachment')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_fields(self)


class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('status', 'priority', 'category', 'assigned_to', 'estimated_resolution')
        widgets = {
            'estimated_resolution': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_fields(self)
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(role__in=[
            CustomUser.Role.ADMIN,
            CustomUser.Role.AGENT,
        ])


class TicketCommentForm(forms.ModelForm):
    attachment = forms.FileField(required=False, label='Fichier ou image')

    class Meta:
        model = TicketComment
        fields = ('message', 'is_internal', 'attachment')
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_fields(self)


class TicketAttachmentForm(forms.ModelForm):
    class Meta:
        model = TicketAttachment
        fields = ('file',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_fields(self)
