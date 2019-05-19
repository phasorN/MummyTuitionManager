from django import forms
from main.models import Student

class StudentCreationForm(forms.ModelForm):
	class Meta:
		model = Student
		fields = ['name', 'grade', 'date_joined', ]

		widgets = {
				'name': forms.TextInput(attrs={'autofocus': True}),
				'date_joined': forms.DateInput(attrs = {'type': 'date', 'class': 'date_field', 'placeholder':"asd"})
			}