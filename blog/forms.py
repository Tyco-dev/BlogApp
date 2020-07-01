from django import forms
from .models import Comment
from django.contrib.auth.models import User


class EmailPostForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)