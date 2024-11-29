
from .serializers import RatingSerializer, MovieRecommendationSerializer
import logging
from django.core.cache import cache
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .services import fetch_movie_recommendations, fetch_movie_details
from rest_framework.exceptions import PermissionDenied
from .models import MovieRating

# Configure loggers for the views module
application_logger = logging.getLogger('application')  # For general application logs
error_logger = logging.getLogger('error')              # For error-specific logs

class RecommendationView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]  # Ensure the user must be authenticated
    serializer_class = MovieRecommendationSerializer

    def get_queryset(self):
        # Since this view doesn't need a queryset, return an empty list or a custom response
        return []

    def post(self, request, *args, **kwargs):
        preferences = request.data
        cache_key = f"recommendations_{preferences}"
        
        # Check cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            application_logger.info(f"Cache hit for recommendations with preferences: {preferences}")
            return Response(cached_data)
        
        # If not in cache, fetch recommendations from TMDb API
        try:
            application_logger.info(f"Fetching movie recommendations for preferences: {preferences}")
            recommendations = fetch_movie_recommendations(
                preferences["genres"],
                preferences["language"],
                preferences["release_year"]
            )
        except Exception as e:
            error_logger.error(f"Error fetching recommendations: {e}", exc_info=True)
            return Response({"error": "Failed to fetch movie recommendations. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Cache the recommendations for 10 minutes
        cache.set(cache_key, recommendations, timeout=600)
        application_logger.info(f"Successfully fetched and cached movie recommendations for preferences: {preferences}")
        return Response(recommendations)


class MovieDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        movie_id = kwargs["movie_id"]
        cache_key = f"movie_{movie_id}"
        
        # Check cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            application_logger.info(f"Cache hit for movie details with ID: {movie_id}")
            return Response(cached_data)
        
        # If not in cache, fetch movie details from TMDb API
        try:
            application_logger.info(f"Fetching details for movie ID: {movie_id}")
            movie_details = fetch_movie_details(movie_id)
        except Exception as e:
            error_logger.error(f"Error fetching movie details for ID {movie_id}: {e}", exc_info=True)
            return Response({"error": "Failed to fetch movie details. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Cache the movie details for 10 minutes
        cache.set(cache_key, movie_details, timeout=600)
        application_logger.info(f"Successfully fetched and cached details for movie ID: {movie_id}")
        return Response(movie_details)


class RatingView(ListCreateAPIView):
    """
    This view handles saving a user's rating for a movie and listing saved ratings.
    """
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]  # Require authentication for creating ratings

    def get_queryset(self):
        """
        Dynamically fetch the queryset based on the authenticated user.
        """
        user = self.request.user
        # Ensure user is authenticated before returning ratings
        if user.is_authenticated:
            return MovieRating.objects.filter(user=user)
        else:
            # Return an empty queryset or raise an error if the user is not authenticated
            return MovieRating.objects.none()

    def perform_create(self, serializer):
        """
        Save the movie rating to the database.
        Ensures that the user is authenticated before saving the rating.
        """
        user = self.request.user
        if user.is_authenticated:
            serializer.save(user=user)
            application_logger.info(f"Saved rating: {serializer.data}")
        else:
            error_logger.error("Anonymous user attempted to save a rating", exc_info=True)
            raise PermissionDenied("You must be logged in to submit a rating.")

    def post(self, request, *args, **kwargs):
        """
        Save a user's rating for a movie and return a confirmation response.
        This method now returns appropriate error messages for unauthenticated users.
        """
        if not request.user.is_authenticated:
            error_logger.error("Anonymous user tried to submit a rating.", exc_info=True)
            raise PermissionDenied("You must be logged in to submit a rating.")

        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            application_logger.info(f"Successfully created rating: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            error_logger.error(f"Failed to create rating. Errors: {serializer.errors}", exc_info=True)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
