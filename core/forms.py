from django import forms

WIDGET_ATTRS = {'class': 'form-input'}


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={**WIDGET_ATTRS, 'placeholder': 'Your name'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={**WIDGET_ATTRS, 'placeholder': 'you@example.com'}),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={**WIDGET_ATTRS, 'placeholder': 'How can we help?', 'rows': 5}),
    )
