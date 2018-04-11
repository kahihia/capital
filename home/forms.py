from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    contact = forms.CharField(max_length = 13 , min_length=10)
    class Meta:
        model = Contact
        exclude = ['datetime']
