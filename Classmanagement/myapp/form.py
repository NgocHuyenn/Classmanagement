from django import forms
from myapp.models import User
from .models import Message
from .models import Assignment

class MessageForm(forms.ModelForm):
    receiver = forms.ModelChoiceField(queryset=User.objects.all(), label="Receiver")

    class Meta:
        model = Message
        fields = ['receiver', 'subject', 'body']

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'file']