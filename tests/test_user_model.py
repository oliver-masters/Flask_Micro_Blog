import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        """
        Feature: password hashing and verification functionality of User.

        Scenario: User sets and verifies their password
            Given a User with no password set
            When the User sets their password to "cat"
            Then the password hash should not contain "cat"
            And the password "dog" should not be verified
            And the password "cat" should be verified
        """
        user_susan = User(username='susan')
        self.assertIsNone(user_susan.password_hash)
        user_susan.set_password('cat')
        self.assertNotIn("cat", user_susan.password_hash)
        self.assertFalse(user_susan.check_password('dog'))
        self.assertTrue(user_susan.check_password('cat'))

    def test_avatar(self):
        """
        Feature: avatar of User

        Scenario: User has default avatar from gravatar.com
            Given a User
            When the User's avatar is called
            Then a URL for a specific Gravatar icon is returned

        """
        user_john = User(username='john', email='john@example.com')
        self.assertEqual(user_john.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        """
        Feature: User follow and unfollow

        Scenario: User can follow and be followed by another other user.
            Given a User "John" and a User "Susan"
            And both users have no followers and follow nobody
            When John follows Susan
            Then John has one "followed" User, and that User is Susan
            And Susan has one "follower" User, and that User is John

        Scenario: User can unfollow another user.
            Given a User "John" and a User "Susan"
            And John has "followed" Susan
            And Susan has followed nobody
            When John unfollows Susan
            Then John has no "followed" Users
            And Susan has no "follower" Users
        """
        user_john = User(username='john', email='john@example.com')
        user_susan = User(username='susan', email='susan@example.com')
        db.session.add(user_john)
        db.session.add(user_susan)
        db.session.commit()
        self.assertEqual(user_john.followed.all(), [])
        self.assertEqual(user_john.followers.all(), [])

        user_john.follow(user_susan)
        db.session.commit()
        self.assertTrue(user_john.is_following(user_susan))
        self.assertEqual(user_john.followed.count(), 1)
        self.assertEqual(user_john.followed.first().username, 'susan')
        self.assertEqual(user_susan.followers.count(), 1)
        self.assertEqual(user_susan.followers.first().username, 'john')

        user_john.unfollow(user_susan)
        db.session.commit()
        self.assertFalse(user_john.is_following(user_susan))
        self.assertEqual(user_john.followed.count(), 0)
        self.assertEqual(user_susan.followers.count(), 0)

    def test_follow_posts(self):
        """
        Feature: Posts of followed Users

        Scenario: Users can view posts of followed Users
            Given a User, David, who follows no Users
            When David views their "followed" posts
            Then David can only view their own posts

            Given a User, Susan, who follows just one User, Mary
            When Susan views their "followed" posts
            Then Susan can view Mary's posts and Susan's posts only

            Given a User, John, who follows two Users, Susan and David
            When John views their "followed" posts
            Then John can view John's, Susan's and David's posts only
        """
        # create four users
        user_john = User(username='john', email='john@example.com')
        user_susan = User(username='susan', email='susan@example.com')
        user_mary = User(username='mary', email='mary@example.com')
        user_david = User(username='david', email='david@example.com')
        db.session.add_all([user_john, user_susan, user_mary, user_david])

        # create four posts
        now = datetime.utcnow()
        post_john = Post(body="post from john", author=user_john,
                  timestamp=now + timedelta(seconds=1))
        post_susan = Post(body="post from susan", author=user_susan,
                  timestamp=now + timedelta(seconds=4))
        post_mary = Post(body="post from mary", author=user_mary,
                  timestamp=now + timedelta(seconds=3))
        post_david = Post(body="post from david", author=user_david,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([post_john, post_susan, post_mary, post_david])
        db.session.commit()

        # setup the followers
        user_john.follow(user_susan)  # john follows susan
        user_john.follow(user_david)  # john follows david
        user_susan.follow(user_mary)  # susan follows mary
        user_mary.follow(user_david)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        john_followed_posts = user_john.followed_posts().all()
        susan_followed_posts = user_susan.followed_posts().all()
        mary_followed_posts = user_mary.followed_posts().all()
        david_followed_posts = user_david.followed_posts().all()

        # John can view Susan's, David's and John's posts, but not Mary's post
        self.assertEqual(john_followed_posts, [post_susan, post_david, post_john])
        self.assertNotIn(post_mary, john_followed_posts)

        # Susan can view Susan's and Mary's posts, but not David's or John's posts
        self.assertEqual(susan_followed_posts, [post_susan, post_mary])
        self.assertNotIn(post_david, susan_followed_posts)
        self.assertNotIn(post_john, susan_followed_posts)

        # Mary can view Mary's and David's posts, but not John's or Susan's posts
        self.assertEqual(mary_followed_posts, [post_mary, post_david])
        self.assertNotIn(post_john, mary_followed_posts)
        self.assertNotIn(post_susan, mary_followed_posts)

        # David can only view David's posts and nobody elses.
        self.assertEqual(david_followed_posts, [post_david])
        self.assertNotIn(post_john, david_followed_posts)
        self.assertNotIn(post_susan, david_followed_posts)
        self.assertNotIn(post_mary, david_followed_posts)

