from django.conf import settings
from django.db import models
from django.utils import timezone
import re

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='카테고리')
    enable_map = models.BooleanField(default=True, verbose_name='지도 활성화')
    enable_due_date = models.BooleanField(default=True, verbose_name='마감일 활성화')
    enable_photo = models.BooleanField(default=True, verbose_name='사진 활성화')
    enable_time = models.BooleanField(default=True, verbose_name='시간 활성화')
    enable_price = models.BooleanField(default=True, verbose_name='가격 활성화')
    enable_tags = models.BooleanField(default=True, verbose_name='태그 활성화')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리'

class Post(models.Model):
    # blog/models.py - add to Post model
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts', verbose_name='태그')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='작성자')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='카테고리')
    title = models.CharField(max_length=200, verbose_name='제목')
    text = models.TextField(verbose_name='내용')
    created_date = models.DateTimeField(default=timezone.now, verbose_name='작성일')
    published_date = models.DateTimeField(blank=True, null=True, verbose_name='게시일')
    latitude = models.FloatField(blank=True, null=True, verbose_name='위도')
    longitude = models.FloatField(blank=True, null=True, verbose_name='경도')
    due_date = models.DateTimeField(blank=True, null=True, verbose_name='마감일시')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='가격')
    related_posts = models.ManyToManyField('self', blank=True, symmetrical=False, 
                                          related_name='tagged_by', verbose_name='관련 게시글')
    
    def publish(self):
        self.published_date = timezone.now()
        self.save()
    
    def __str__(self):
        return self.title
    
    def extract_tags(self):
        """Extract @username mentions from text"""
        pattern = r'@(\w+)'
        return re.findall(pattern, self.text)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Process tags after saving
        if self.text:
            # Extract usernames from @mentions
            usernames = self.extract_tags()
            # Get users that were mentioned
            if usernames:
                from django.contrib.auth.models import User
                mentioned_users = User.objects.filter(username__in=usernames)
                
                # Create notifications for mentioned users
                for user in mentioned_users:
                    if user != self.author:  # Don't notify yourself
                        Notification.objects.create(
                            user=user,
                            message=f"@{self.author.username}님이 게시글에서 언급했습니다: {self.title}",
                            related_post=self
                        )
                
                # Get posts by mentioned users
                mentioned_posts = Post.objects.filter(author__username__in=usernames).exclude(pk=self.pk)
                if mentioned_posts.exists():
                    # Add them as related posts
                    self.related_posts.add(*mentioned_posts)
    
    class Meta:
        verbose_name = '게시글'
        verbose_name_plural = '게시글'

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', verbose_name='게시글')
    image = models.ImageField(upload_to='blog/%Y/%m/%d/', verbose_name='이미지')
    
    def __str__(self):
        return f"{self.post.title}의 이미지"
    
    class Meta:
        verbose_name = '게시글 이미지'
        verbose_name_plural = '게시글 이미지'

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

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name='사용자')
    message = models.CharField(max_length=255, verbose_name='메시지')
    related_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, verbose_name='관련 게시글')
    is_read = models.BooleanField(default=False, verbose_name='읽음 여부')
    created_date = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = '알림'
        verbose_name_plural = '알림'
        
    def __str__(self):
        return self.message

class PushSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_subscriptions', verbose_name='사용자')
    subscription_info = models.JSONField(verbose_name='구독 정보')
    created_date = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    
    class Meta:
        verbose_name = '푸시 구독'
        verbose_name_plural = '푸시 구독'
        
    def __str__(self):
        return f"{self.user.username}의 푸시 구독"

# blog/models.py - add this model
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '태그'
        verbose_name_plural = '태그'