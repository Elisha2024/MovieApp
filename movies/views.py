from .serializers import RatingSerializer, MovieRecommendationSerializer
import logging
from django.core.cache import cache
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .services import fetch_movie_recommendations, fetch_movie_details
from rest_framework.exceptions import PermissionDenied
from .models import MovieRating
from .utils import build_response, CustomPagination



# Configure loggers for the views module
application_logger = logging.getLogger('application')
error_logger = logging.getLogger('error')


class RecommendationView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MovieRecommendationSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return []

    def post(self, request, *args, **kwargs):
        preferences = request.data

        # Check if required preferences are provided
        if not preferences.get("genres") or not preferences.get("language"):
            return build_response(
                errors={"preferences": "Missing required preferences."},
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Missing preferences."
            )
        

        cache_key = f"recommendations_{preferences}"

        # Check cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            application_logger.info(f"Cache hit for recommendations with preferences: {preferences}")
            return build_response(data=cached_data, message="Recommendations fetched from cache.")

        # Fetch recommendations
        try:
            application_logger.info(f"Fetching movie recommendations for preferences: {preferences}")
            recommendations = fetch_movie_recommendations(
                preferences.get("genres"),
                preferences.get("language"),
                preferences.get("release_year"),
            )
        except KeyError as e:
            error_logger.error(f"Invalid preferences data: {e}", exc_info=True)
            return build_response(
                errors={"preferences": "Invalid preferences format."},
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid data."
            )
        except Exception as e:
            error_logger.error(f"Error fetching recommendations: {e}", exc_info=True)
            return build_response(
                errors={"detail": "Failed to fetch movie recommendations."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Internal Server Error."
            )

        # Cache recommendations for future requests
        cache.set(cache_key, recommendations, timeout=600)
        application_logger.info(f"Successfully fetched and cached movie recommendations for preferences: {preferences}")
        return build_response(data=recommendations, message="Movie recommendations retrieved successfully.")

class MovieDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        movie_id = kwargs.get("movie_id")
        cache_key = f"movie_{movie_id}"

        # Check cache
        cached_data = cache.get(cache_key)
        if cached_data:
            application_logger.info(f"Cache hit for movie details with ID: {movie_id}")
            return build_response(data=cached_data, message="Movie details fetched from cache.")

        # Fetch movie details
        try:
            application_logger.info(f"Fetching details for movie ID: {movie_id}")
            movie_details = fetch_movie_details(movie_id)
        except Exception as e:
            error_logger.error(f"Error fetching movie details for ID {movie_id}: {e}", exc_info=True)
            return build_response(errors={"detail": "Failed to fetch movie details."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Internal Server Error.")

        cache.set(cache_key, movie_details, timeout=600)
        application_logger.info(f"Successfully fetched and cached details for movie ID: {movie_id}")
        return build_response(data=movie_details, message="Movie details retrieved successfully.")


class RatingView(ListCreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return MovieRating.objects.filter(user=user)
        return MovieRating.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
            serializer.save(user=user)
            application_logger.info(f"Saved rating: {serializer.data}")
        else:
            error_logger.error("Anonymous user attempted to save a rating", exc_info=True)
            raise PermissionDenied("You must be logged in to submit a rating.")

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            error_logger.error("Anonymous user tried to submit a rating.", exc_info=True)
            return build_response(errors={"detail": "Authentication required."}, status_code=status.HTTP_403_FORBIDDEN, message="You must be logged in to submit a rating.")

        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            application_logger.info(f"Successfully created rating: {serializer.data}")
            return build_response(data=serializer.data, message="Rating submitted successfully.", status_code=status.HTTP_201_CREATED)
        else:
            error_logger.error(f"Failed to create rating. Errors: {serializer.errors}", exc_info=True)
            return build_response(errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST, message="Invalid rating data.")
