from django import forms

from .models import Playlist


class PlaylistForm(forms.ModelForm):
    """Validate the editable details of a user's private playlist."""

    class Meta:
        model = Playlist
        fields = ['title', 'description']
        error_messages = {
            'title': {'required': 'Enter a playlist name.'},
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Playlist name',
                'maxlength': 150,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Optional description',
                'rows': 4,
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('Enter a playlist name.')
        return title

    def clean_description(self):
        return self.cleaned_data.get('description', '').strip()
