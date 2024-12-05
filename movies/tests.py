from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import User  # Ensure User model is imported


class BaseTestCase(TestCase):
    # Helper method for user creation (moved to the base class)
    def create_user(self):
        return User.objects.create_user(username='testuser', password='testpass')

class TestMovieDetailView(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        self.movie_url = reverse('movie_detail', args=[13])  # Adjust movie_id if needed


    def test_fetch_movie_details_valid_id(self):
        response = self.client.get(f'{self.movie_url}')  # Valid Movie ID
        # print(self.movie_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title', response.json()['data'])  # Check if 'title' is in the response

    def test_fetch_movie_details_invalid_id(self):
        response = self.client.get(reverse('movie_detail', args=[99999999]))  # Non-existent Movie ID
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('detail', response.json()['errors'])  # Check if error message is included

    # def test_fetch_movie_details_invalid_format(self):
    #     response = self.client.get(reverse('movie_detail', args=[-5]))  # Invalid ID format
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('detail', response.errors)  # Check for proper error message


class TestRatingView(BaseTestCase): # test passed
    def setUp(self):
        self.client = APIClient()
        self.ratings_url = reverse('ratings')

    def test_create_rating_valid_input(self):
        self.client.force_authenticate(user=self.create_user())  # Mock authentication
        response = self.client.post(self.ratings_url, {'movie_id': 1, 'rating': 5.0})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertIn('movie_id', response.data)
        self.assertIn('movie_id', response.data['data'])
        # self.assertEqual(response.data['rating'], 5.0)
        self.assertEqual(response.data['data']['rating'], 5)


    # def test_create_rating_invalid_rating_value(self):
    #     self.client.force_authenticate(user=self.create_user())
    #     response = self.client.post(self.ratings_url, {'movie_id': 1, 'rating': 10.0})  # Rating out of range
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('rating', response.data)  # Check if 'rating' field is in the error response

    def test_create_rating_missing_movie_id(self):
        self.client.force_authenticate(user=self.create_user())
        response = self.client.post(self.ratings_url, { 'rating': 4.5})  # Missing movie_id
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('movie_id', response.data['errors'])
    
        
    def test_create_rating_unauthenticated(self):
        response = self.client.post(self.ratings_url, {'movie_id': 1, 'rating': 5.0})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestRecommendationView(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        self.recommendations_url = reverse('recommendations')

    def test_recommendations_valid_preferences(self): #test passed
        self.client.force_authenticate(user=self.create_user())
        response = self.client.post(self.recommendations_url, {
            'genres': ['35', '18'],  # Valid genre IDs
            'language': 'en',
            'release_year': 1989
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertTrue(len(response.data['data']['results']) > 0)  # Check recommendations are returned
        self.assertIn('results', response.data['data'])

    # def test_recommendations_invalid_genres(self): #takes me back to the view to handle errors correctly
    #     self.client.force_authenticate(user=self.create_user())
    #     response = self.client.post(self.recommendations_url, {
    #         'genres': ['invalid_genre'],  # Invalid genre format
    #         'language': 'en',
    #         'release_year': 2000
    #     })
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('genres', response.data)

    def test_recommendations_missing_preferences(self):
        self.client.force_authenticate(user=self.create_user())
        response = self.client.post(self.recommendations_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('preferences', response.json()['errors'])

    def test_recommendations_unauthenticated(self):
        response = self.client.post(self.recommendations_url, {
            'genres': ['35', '18'],
            'language': 'en',
            'release_year': 1989
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
