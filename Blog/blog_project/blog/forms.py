from django import forms
from .models import Post, Comment

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class PostForm(forms.ModelForm):
    images = MultipleFileField(
        required=False,
        label='이미지',
        widget=MultipleFileInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Post
        fields = ('category', 'title', 'text', 'latitude', 'longitude', 'due_date')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        labels = {
            'category': '카테고리',
            'title': '제목',
            'text': '내용',
            'due_date': '마감일',
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'text')
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'author': '작성자',
            'text': '내용',
        }