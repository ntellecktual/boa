# boaapp/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Document


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('uploaded_file',)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text=_('Required. Please enter a valid email address.'))
    # You might add other custom fields here

    class Meta(UserCreationForm.Meta):
        model = User  # Or your custom user model
        # *** Ensure the standard fields AND your custom ones are listed ***
        # UserCreationForm.Meta.fields includes ('username', 'password', 'password2')
        fields = (
            UserCreationForm.Meta.fields + ('email',)
        )  # Make sure 'username', 'password', 'password2' are implicitly included or explicitly listed if you override completely.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help_text to fields after initialization if needed
        if 'username' in self.fields:
            self.fields['username'].help_text = _(
                'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
            )
        if 'password2' in self.fields:
            self.fields['password2'].help_text = _('Enter the same password as before, for verification.')
        # Add help text for password1 if desired (often handled by validators)
        # if 'password1' in self.fields:
        #    self.fields['password1'].help_text = _('Password must meet complexity requirements...')
