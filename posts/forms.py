from django import forms
from posts.models import Post


class PostForm(forms.ModelForm):
    """ form for adding a new post """
    class Meta:
        """ bind form to Post model and add fields 'text' and 'group' """
        model = Post
        fields = ('text', 'group')
        labels = {'text': 'Текст записи', 'group':'Сообщество'}
        widgets = {'text': forms.Textarea()}
