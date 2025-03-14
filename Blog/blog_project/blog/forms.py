from django import forms
from .models import Post, Comment

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['multiple'] = True
        return context

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
        fields = ('category', 'title', 'text', 'latitude', 'longitude', 'due_date', 'price')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
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