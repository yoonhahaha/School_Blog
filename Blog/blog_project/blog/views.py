from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Post, Comment, Category, PostImage, Notification, PushSubscription
from .forms import PostForm, CommentForm
from django.db import models
from django.http import JsonResponse
from datetime import datetime
from django.contrib.auth.models import User
from django.urls import reverse
import json
from webpush import send_user_notification

@login_required
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    categories = Category.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts, 'categories': categories})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@csrf_exempt
@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # Handle category-based settings
            category = form.cleaned_data.get('category')
            if category:
                if not category.enable_map:
                    post.latitude = None
                    post.longitude = None
                
                if not category.enable_due_date:
                    post.due_date = None
            
            post.save()
            
            # Handle time component based on category settings
            if category and not category.enable_time and post.due_date:
                # Set time to midnight if time is disabled
                post.due_date = timezone.make_aware(
                    datetime.combine(post.due_date.date(), datetime.min.time())
                )
                post.save()
            
            # Save multiple images
            for image in request.FILES.getlist('images'):
                PostImage.objects.create(post=post, image=image)
            
            # Create notifications for all users except the author
            users = User.objects.exclude(id=request.user.id)
            for user in users:
                # Create database notification
                Notification.objects.create(
                    user=user,
                    message=f"새 게시글: {post.title}",
                    related_post=post
                )
                
                # Send push notification
                post_url = request.build_absolute_uri(reverse('post_detail', kwargs={'pk': post.pk}))
                send_push_notification(
                    user=user,
                    title="새 게시글 알림",
                    body=f"{request.user.username}님이 '{post.title}' 게시글을 작성했습니다.",
                    url=post_url
                )
                
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

@csrf_exempt
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # Handle category-based settings
            category = form.cleaned_data.get('category')
            if category:
                if not category.enable_map:
                    post.latitude = None
                    post.longitude = None
                
                if not category.enable_due_date:
                    post.due_date = None
            
            post.save()
            
            # Handle time component based on category settings
            if category and not category.enable_time and post.due_date:
                # Set time to midnight if time is disabled
                post.due_date = timezone.make_aware(
                    datetime.combine(post.due_date.date(), datetime.min.time())
                )
                post.save()
            
            # Handle new image uploads
            for image in request.FILES.getlist('images'):
                PostImage.objects.create(post=post, image=image)
                
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form, 'post': post})

@csrf_exempt
@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@csrf_exempt
@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')

@csrf_exempt
@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.approved_comment = True  # Auto-approve comments
            comment.save()
            
            # Create notification for post author
            if request.user != post.author:
                # Create database notification
                Notification.objects.create(
                    user=post.author,
                    message=f"{request.user.username}님이 댓글을 작성했습니다: {post.title}",
                    related_post=post
                )
                
                # Send push notification
                post_url = request.build_absolute_uri(reverse('post_detail', kwargs={'pk': post.pk}))
                send_push_notification(
                    user=post.author,
                    title="새 댓글 알림",
                    body=f"{request.user.username}님이 '{post.title}' 게시글에 댓글을 작성했습니다.",
                    url=post_url
                )
    return redirect('post_detail', pk=post.pk)

@csrf_exempt
@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@csrf_exempt
@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)

@csrf_exempt
@login_required
def category_posts(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    posts = Post.objects.filter(category=category, published_date__lte=timezone.now()).order_by('-published_date')
    categories = Category.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts, 'categories': categories, 'category': category})

@csrf_exempt
@login_required
def search_results(request):
    query = request.GET.get('q', '')
    if query:
        posts = Post.objects.filter(
            models.Q(title__icontains=query) | 
            models.Q(text__icontains=query) |
            models.Q(author__username__icontains=query) |
            models.Q(category__name__icontains=query)
        ).filter(published_date__lte=timezone.now()).order_by('-published_date')
    else:
        posts = Post.objects.none()
    
    categories = Category.objects.all()
    return render(request, 'blog/search_results.html', {
        'posts': posts, 
        'categories': categories, 
        'query': query
    })

@csrf_exempt
def category_settings(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    return JsonResponse({
        'enable_map': category.enable_map,
        'enable_due_date': category.enable_due_date,
        'enable_photo': category.enable_photo,
        'enable_time': category.enable_time,
        'enable_price': category.enable_price
    })
@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'blog/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    
    if notification.related_post:
        return redirect('post_detail', pk=notification.related_post.pk)
    return redirect('notifications')

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')

@csrf_exempt
@login_required
def subscribe_push(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            subscription_info = data.get('subscription')
            
            # Save or update subscription
            subscription, created = PushSubscription.objects.get_or_create(
                user=request.user,
                defaults={'subscription_info': subscription_info}
            )
            
            if not created:
                subscription.subscription_info = subscription_info
                subscription.save()
                
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def send_push_notification(user, title, body, url):
    """Helper function to send web push notifications"""
    payload = {
        'title': title,
        'body': body,
        'url': url
    }
    
    try:
        subscriptions = PushSubscription.objects.filter(user=user)
        for subscription in subscriptions:
            send_user_notification(
                user=user,
                payload=payload, 
                ttl=1000,
                subscription_info=subscription.subscription_info
            )
        return True
    except Exception as e:
        print(f"Push notification error: {str(e)}")
        return False