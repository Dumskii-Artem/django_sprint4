from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment

User = get_user_model()


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        exclude = ['author', ]
        widgets = {'pub_date': forms.DateInput(attrs={'type': 'date'})}
        # widgets = {
        #     'pub_date': forms.DateInput(attrs={'type': 'date'}),
        #     'text': forms.Textarea(attrs={'rows': 4, 'cols': 50})}


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
