import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post
from flask_login import FlaskLoginClient
from bs4 import BeautifulSoup


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        app.test_client_class = FlaskLoginClient
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_homepage_no_login(self):
        """
        Feature: Homepage defaults to Login screen when not logged in

        Scenario: Request homepage with no user logged in
            Given user isn't logged in
            When accessing the homepage, "/"
            Then the page is redirected to the login page, "/login"
            And the page contains the phrase "Sign In"
        """
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.request.path, "/login")
        self.assertIn(b"<h1>Sign In</h1>", response.data)

    def test_homepage_with_login(self):
        """
        Feature: Homepage is viewed when user is logged in

        Scenario: Request homepage with user logged in
            Given user, "susan", is logged in
            When accessing the homepage, "/"
            Then the response path is "/"
            And the page contains the phrase "Hi, susan!"
        """
        user_susan = User(username='susan')
        user_susan.set_password('cat')
        db.session.add(user_susan)
        db.session.commit()

        with app.test_client(user=user_susan) as client:
            response = client.get("/", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.request.path, "/")
            self.assertIn(b"<h1>Hi, susan!</h1>", response.data)

    def test_create_post(self):
        """
        Feature: User can create post

        Scenario: Post is created by user
            Given user, "susan", is logged in
            When susan creates a post
            Then the post is saved to db
            And homepage is displayed
            And a message is displayed to say the post is now live
            And the post is displayed on the homepage
        """
        user_susan = User(username='susan', email="susan@test.com")
        user_susan.set_password('cat')
        db.session.add(user_susan)
        db.session.commit()

        with app.test_client(user=user_susan) as client:
            response = client.get("/")
            soup = BeautifulSoup(response.data, "html.parser")
            csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

            data = {"post": "This is my first post!", "csrf_token": csrf_token}
            response = client.post("/", data=data, follow_redirects=True)

            posts = Post.query.all()
            self.assertEqual(len(posts), 1)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.request.path, "/index")

            self.assertIn(b"Your post is now live!", response.data)
            self.assertIn(b"This is my first post!", response.data)
