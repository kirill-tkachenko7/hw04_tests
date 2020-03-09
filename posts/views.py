from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import PostForm
from .models import Post, Group, User


def index(request):
    """ display latest posts """
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) 

    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number) 
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    """ display latest posts in the group """

    group = get_object_or_404(Group, slug=slug)

    post_list = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    """display a form for adding a new post to authenticated users"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            # if form is valid, populate missing data and save a post
            # all validation is done at the model level
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    """ profile information and user's latest posts """
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=profile).order_by("-pub_date").all()
    
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number)

    context_dict =  {
        'profile': profile,
        'post_count': post_list.count(),
        'page': page, 
        'paginator': paginator
    }
    return render(request, 'profile.html', context_dict)


def post_view(request, username, post_id):
    """ view a post """
    # cache the author so that template doesn't 
    # query the database for each {{ post.author }} tag.
    # if post or author not found, or author's username is wrong, return 404.
    post_object = get_object_or_404(Post.objects.select_related('author'), 
        id=post_id, author__username=username)
    
    post_count = Post.objects.filter(author=post_object.author).all().count()

    context_dict =  {
        'profile': post_object.author,
        'post_count': post_count,
        'post': post_object
    }
    return render(request, "post.html", context_dict)


def post_edit(request, username, post_id):
    # only post author can edit post
    if request.user.username != username:
        return redirect('post', username=username, post_id=post_id)

    # get post to be edited
    # return 404 if User with username does not exist, if Post with 
    # post_id does not exist or if username is not the author of the Post.
    post_object = get_object_or_404(Post, id=post_id, author__username=username)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post_object)
        if form.is_valid():
            form.save()
            return redirect('post', username=username, post_id=post_id)
        return render(request, 'edit_post.html', {'form': form, 'post': post_object})

    form = PostForm(instance=post_object)
    return render(request, 'edit_post.html', {'form': form, 'post': post_object})