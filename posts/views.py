from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import PostForm
from .models import Post, Group, User


def index(request):
    """ display latest posts """
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # display 10 posts per page

    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number) # retreive posts with correct offset
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    """ display latest posts in the group """

    # get group object using a slug passed in the URL
    group = get_object_or_404(Group, slug=slug)

    # show 10 posts per page
    post_list = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    """display a form for adding a new post to authenticated users"""
    if request.method == 'POST':
        # if we got a POST request, validate form
        form = PostForm(request.POST)
        if form.is_valid():
            # if form is valid, populate missing data and save a post
            # all validation is done at the model level
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # redirect user to the home page
            return redirect('index')
        # if form is not valid, display the same form and show validation errors
        return render(request, 'new_post.html', {'form': form})
    # if this is not a POST request, display a blank PostForm
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    """ profile information and user's latest posts """
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=profile).order_by("-pub_date").all()
    
    paginator = Paginator(post_list, 10) # display 10 posts per page
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number) # retreive posts with correct offset

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
    
    # count author's posts:
    post_count = Post.objects.filter(author=post_object.author).all().count()

    context_dict =  {
        'profile': post_object.author,
        'post_count': post_count,
        'post': post_object
    }
    return render(request, "post.html", context_dict)


@login_required
def post_edit(request, username, post_id):
    # only post author can edit post
    if request.user.username != username:
        return redirect('post', username=username, post_id=post_id)

    # get post to be edited
    # return 404 if User with username does not exist, if Post with 
    # post_id does not exist or if username is not the author of the Post.
    post_object = get_object_or_404(Post, id=post_id, author__username=username)

    if request.method == 'POST':
        # if we got a POST request, validate form
        form = PostForm(request.POST, instance=post_object)
        if form.is_valid():
            # if form is valid, save changes
            form.save()
            # redirect to post_view
            return redirect('post', username=username, post_id=post_id)
        # if form is not valid, display the same form and show validation errors
        return render(request, 'new_post.html', {'form': form})

    # if this is not a POST request, pre-populate form with post object's data.
    form = PostForm(instance=post_object)
    return render(request, 'new_post.html', {'form': form, 'post': post_object})