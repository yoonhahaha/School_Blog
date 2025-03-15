from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    tag_string = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '태그 (쉼표로 구분)'}),
        label='태그'
    )
    
    class Meta:
        model = Post
        fields = ('category', 'title', 'text', 'latitude', 'longitude', 'due_date', 'price')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'data-mention': 'true'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'category': '카테고리',
            'title': '제목',
            'text': '내용',
            'due_date': '마감일시',
            'price': '가격',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        # Get the current category (either from instance or initial data)
        category = None
        if instance and instance.pk:
            category = instance.category
            # Set initial value for tag_string if instance has tags
            self.initial['tag_string'] = ', '.join([tag.name for tag in instance.tags.all()])
        elif 'initial' in kwargs and 'category' in kwargs['initial']:
            category_id = kwargs['initial']['category']
            from .models import Category
            try:
                category = Category.objects.get(id=category_id)
            except:
                pass
        
        if category:
            # Set appropriate input type for due_date based on enable_time setting
            if not category.enable_time and 'due_date' in self.fields:
                self.fields['due_date'].widget = forms.DateInput(
                    attrs={'class': 'form-control', 'type': 'date'}
                )
                self.fields['due_date'].label = '마감일'
                
            # Show/hide tag field based on category settings
            if not category.enable_tags and 'tag_string' in self.fields:
                self.fields['tag_string'].widget = forms.HiddenInput()


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