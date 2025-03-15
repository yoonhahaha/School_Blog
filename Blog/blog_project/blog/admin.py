from django.contrib import admin
from django.db import connection
from .models import Post, Comment, Category, Notification, PushSubscription

# blog/admin.py - update CategoryAdmin class
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'enable_map', 'enable_due_date', 'enable_photo', 'enable_time', 'enable_price', 'enable_tags')
    list_editable = ('enable_map', 'enable_due_date', 'enable_photo', 'enable_time', 'enable_price', 'enable_tags')
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_date', 'published_date', 'due_date', 'price')
    list_filter = ('created_date', 'published_date', 'due_date', 'author')
    search_fields = ('title', 'text')
    date_hierarchy = 'created_date'
    
    def delete_model(self, request, obj):
        # Delete related notifications
        Notification.objects.filter(related_post=obj).delete()
        
        # Delete any existing post images (if the table still exists)
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM blog_postimage WHERE post_id = %s", [obj.id])
        except:
            pass
        
        # Delete comments
        Comment.objects.filter(post=obj).delete()
        
        # Now delete the post
        obj.delete()
    
    def delete_queryset(self, request, queryset):
        # For bulk deletions
        for obj in queryset:
            self.delete_model(request, obj)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_date', 'approved_comment')
    list_filter = ('approved_comment', 'created_date')
    search_fields = ('author', 'text')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'related_post', 'is_read', 'created_date')
    list_filter = ('is_read', 'created_date')
    search_fields = ('user__username', 'message')

class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_date')
    list_filter = ('created_date',)
    search_fields = ('user__username',)

admin.site.register(PushSubscription, PushSubscriptionAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Notification, NotificationAdmin)