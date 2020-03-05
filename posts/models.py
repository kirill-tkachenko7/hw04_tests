from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    # Group name
    title = models.CharField(max_length=200)

    # Part of the URL of the group (/group/<slug>). 
    # Must be unique
    slug = models.SlugField(unique=True, allow_unicode=True)

    # Description of the group (more detailed than a title).
    # Max length not limited, we rely on our admins' 
    # common sense to not make massive descriptions
    description = models.TextField()

    def __str__(self):
       # print group title
       return self.title


class Post(models.Model):
    # Content of the post
    text = models.TextField()

    # Date of post publication, default = now
    pub_date = models.DateTimeField(
        verbose_name="date published", auto_now_add=True)
    
    # Author of the post. Must be a registered user
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_author")
    
    # A group where post is posted. A post does not need to belong to a group
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, related_name="post_group", 
        blank=True, null=True)
    
    def __str__(self):
       # print post text
       return self.text