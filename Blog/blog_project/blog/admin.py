from django.contrib import admin
from .models import Post, Comment, Category, PostImage, Notification

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 3

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'enable_map', 'enable_due_date', 'enable_photo', 'enable_time')
    list_editable = ('enable_map', 'enable_due_date', 'enable_photo', 'enable_time')
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_date', 'published_date', 'due_date')
    list_filter = ('created_date', 'published_date', 'due_date', 'author')
    search_fields = ('title', 'text')
    date_hierarchy = 'created_date'
    inlines = [PostImageInline]

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_date', 'approved_comment')
    list_filter = ('approved_comment', 'created_date')
    search_fields = ('author', 'text')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'related_post', 'is_read', 'created_date')
    list_filter = ('is_read', 'created_date')
    search_fields = ('user__username', 'message')

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(PostImage)
admin.site.register(Notification, NotificationAdmin)