from django.test import TestCase, Client
from posts.models import Post, User

# TODO restructure all tests 
class PostsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sarah', email='connor.s@skynet.com', password='12345'
        )
        self.post = Post.objects.create(text="You're talking about things I haven't done yet in the past tense. It's driving me crazy!", author=self.user)

    def test_profile(self):
        """ test that there is a user profile page for each user """
        response = self.client.get('/sarah/')
        self.assertEqual(response.status_code, 200, "profile page does not exist")
        self.assertEqual(len(response.context['page']), 1, "new post is not displayed on profile page")
        self.assertIsInstance(response.context['profile'], User)
        self.assertEqual(response.context['profile'].username, self.user.username, "wrong profile displayed")
    
    def test_add_post_authenticated(self):
        """ test that authenticated user can add new posts """
        if self.client.login(username='sarah', password='12345'):
            response = self.client.get('/new/')
            self.assertEqual(response.status_code, 200, 'Authenticated user must be able to add posts')
        else:
            self.assertTrue(False, 'Failed to authenticate test user')

    def test_add_post_anonymous(self):
        """ test that anonymous user cannot add new posts and is redirected to home page """
        self.client.logout()
        response = self.client.get('/new/')
        self.assertRedirects(response, 
            '/auth/login/?next=/new/',  
            msg_prefix="anonymous user is not redirected to login page")
    
    def test_post_home(self):
        """ test that new post appears on the home page """
        response = self.client.get('/')
        self.assertIn(self.post, 
            response.context['page'], 
            'new post must appear on the home page')
        self.assertEqual(self.post, 
            response.context['page'][0],
            "psot text is on the home page is incorrect")

    def test_post_profile(self):
        """ test that new post appears on author's profile page """
        response = self.client.get(f'/sarah/')
        self.assertIn(self.post, 
            response.context['page'], 
            "new post must appear on the author's profile page")
        self.assertEqual(self.post, 
            response.context['page'][0],
            "post text is on the author's profile page is incorrect")
        
    def test_post_view(self):
        """ test that post appears on post view page """
        response = self.client.get(f'/sarah/{self.post.id}/')

        # test that post page exists
        self.assertEqual(response.status_code, 200, "post page does not exist")

        # test that the right post is displayed
        self.assertEqual(self.post, 
            response.context['post'], 
            "new post must appear on post view page")

class PostEditTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='john', email='connor.j@skynet.com', password='54321')
        self.post = Post.objects.create(text="You gotta listen the way people talk: you don't say \"affirmitive\", or some shit like that, you say \"no problemo\". And if someone comes up to with an attitude you say \"eat me\", and if you wanna shine them on it: \"Hasta la vista baby\".", author=self.user)

    def test_edit_post_anonymous(self):
        self.client.logout()
        response = self.client.get(f'/john/{self.post.id}/edit/')
        self.assertRedirects(response,
            f'/john/{self.post.id}/',
            msg_prefix='anonymous user is not redirected to post view')

    def test_edit_post_wrong_user(self):
        user = User.objects.create_user(username='not_an_author', email='test@mail.ru', password='qwerty')
        if self.client.login(username='not_an_author', password='qwerty'):
            response = self.client.get(f'/john/{self.post.id}/edit/')
            self.assertRedirects(response,
                f'/john/{self.post.id}/',
                msg_prefix='wrong user is not redirected to post view')
        else:
            self.assertTrue(False, 'Failed to authenticate test user')
                
    def test_edit_post_authenticated(self):
        if self.client.login(username='john', password='54321'):
            response = self.client.get(f'/john/{self.post.id}/edit/')
            self.assertEqual(response.status_code, 200, 'Authenticated user must be able to edit posts')

            # edit post and test that it was updated in the db
            orig_text = self.post.text
            new_text = "That's great see your getting it. И немного кириллицы для остроты ощущений"
            self.client.post(f'/john/{self.post.id}/edit/', {'text': new_text})
            self.post.refresh_from_db() # reload post after it was updated
            self.assertEqual(self.post.text, new_text)
            
            # import django.utils.html.escape to account for special characters
            # which are escaped by default in template variables
            # https://code.djangoproject.com/wiki/AutoEscaping
            from django.utils.html import escape
            
            # check that changes are reflected on home page, author's profile and post page
            for url in ('/', '/john/', f'/john/{self.post.id}/'):
                response = self.client.get(url)
                self.assertContains(response,
                    escape(self.post.text), 
                    msg_prefix=f'updates were not reflected in {url}')
                
                # make sure existing post is edited, not a new one added
                self.assertNotContains(response, 
                    escape(orig_text), 
                    msg_prefix=f'old post text remains in {url}')

        else:
            self.assertTrue(False, 'Failed to authenticate test user')