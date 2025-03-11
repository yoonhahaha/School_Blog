from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='카테고리')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리'


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='작성자')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='카테고리')
    title = models.CharField(max_length=200, verbose_name='제목')
    text = models.TextField(verbose_name='내용')
    created_date = models.DateTimeField(default=timezone.now, verbose_name='작성일')
    published_date = models.DateTimeField(blank=True, null=True, verbose_name='게시일')
    image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True, null=True, verbose_name='이미지')
    
    def publish(self):
        self.published_date = timezone.now()
        self.save()
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = '게시글'
        verbose_name_plural = '게시글'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='게시글')
    author = models.CharField(max_length=200, verbose_name='작성자')
    text = models.TextField(verbose_name='내용')
    created_date = models.DateTimeField(default=timezone.now, verbose_name='작성일')
    approved_comment = models.BooleanField(default=False, verbose_name='승인 여부')
    
    def approve(self):
        self.approved_comment = True
        self.save()
    
    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name = '댓글'
        verbose_name_plural = '댓글'