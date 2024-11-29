# movies/urls.py
from django.urls import path
from .views import RecommendationView, MovieDetailView, RatingView

urlpatterns = [
    path('api/recommendations/', RecommendationView.as_view(), name='recommendations'),
    path('api/movie/<int:movie_id>/', MovieDetailView.as_view(), name='movie_detail'),
    path('api/ratings/', RatingView.as_view(), name='ratings'),
]
