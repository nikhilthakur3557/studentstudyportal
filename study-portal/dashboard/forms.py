from django import forms
from dashboard.models import Notes,HomeWork,Todo
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from django.utils.timezone import now
class Noteform(forms.ModelForm):
    class Meta:
        model=Notes
        fields=['title','description']
        
        
class DateInput(forms.DateInput):
    input_type = 'date'  # Use HTML5 date input

    def _init_(self, *args, **kwargs):
        kwargs['attrs'] = kwargs.get('attrs', {})
        kwargs['attrs']['min'] = now().strftime('%Y-%m-%d')  # Set the minimum date to today
        super()._init_(*args, **kwargs)
        
class HomeworkForm(forms.ModelForm):
    class Meta:
        model=HomeWork
        fields=['subject','title','description','due','is_finished']
        widgets = {
            'due': DateInput()  # Properly applying the DateInput widget to the 'due' field
        }
    def clean_due(self):
        due_date = self.cleaned_data.get('due')
        if due_date and due_date < now().date():
            raise forms.ValidationError("The due date cannot be in the past.")
        return due_date


class DashboardForm(forms.Form):
    text=forms.CharField(max_length=100,label="Enter your search")
    
class Todoform(forms.ModelForm):
    class Meta:
        model=Todo
        fields=['title','is_finished']
        
class UserRegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','password1','password2']
        