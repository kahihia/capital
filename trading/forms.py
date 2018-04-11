from django import forms
from account.models import MyUser

class EditProfileForm(forms.Form):
	email = forms.EmailField(max_length=254 , min_length = 5)
	phone = forms.CharField(max_length = 13 , min_length = 10)
	first_name = forms.CharField(max_length = 30)
	last_name = forms.CharField(max_length = 30, required = False)

	def clean_first_name(self):
		if self.cleaned_data['first_name'] is None:
			raise forms.ValidationError('enter valid first name')
		return self.cleaned_data['first_name']