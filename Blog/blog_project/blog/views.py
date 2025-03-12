from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Post, Comment, Category, PostImage
from .forms import PostForm, CommentForm
from django.db import models
from django.http import JsonResponse
from datetime import datetime

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    categories = Category.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts, 'categories': categories})

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
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.approved_comment = True  # Auto-approve comments
            comment.save()
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
def category_posts(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    posts = Post.objects.filter(category=category, published_date__lte=timezone.now()).order_by('-published_date')
    categories = Category.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts, 'categories': categories, 'category': category})

@csrf_exempt
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
        'enable_time': category.enable_time
    })