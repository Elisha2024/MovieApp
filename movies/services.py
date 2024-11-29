import logging
import requests
from decouple import config

# Set up loggers for the service layer
application_logger = logging.getLogger('application')  # For general application logs
error_logger = logging.getLogger('error')              # For error-specific logs

TMDB_API_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = config("TMDB_API_KEY")


class MovieRecommendationError(Exception):
    """Custom exception for movie recommendation fetch errors."""
    pass


def fetch_movie_recommendations(genres, language, release_year):
    """
    Fetch movie recommendations from TMDb API based on provided criteria.
    
    :param genres: List of genres
    :param language: Language code
    :param release_year: Release year
    :return: Dictionary containing recommendations
    """
    application_logger.info(f"Fetching movie recommendations for genres: {genres}, language: {language}, release_year: {release_year}")
    url = f"{TMDB_API_URL}/discover/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'language': language,
        'with_genres': ",".join(genres),
        'primary_release_year': release_year
    }
    try:
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        recommendations = response.json()
        application_logger.info(f"Successfully fetched {len(recommendations.get('results', []))} movie recommendations.")
        return recommendations
    except requests.exceptions.HTTPError as e:
        error_logger.error(f"HTTPError fetching recommendations: {e}", exc_info=True)
        raise MovieRecommendationError("Could not fetch movie recommendations. Please try again later.")
    except requests.exceptions.RequestException as e:
        error_logger.error(f"RequestException fetching recommendations: {e}", exc_info=True)
        raise MovieRecommendationError("An error occurred while fetching recommendations. Please try again.")
    except Exception as e:
        error_logger.error(f"Unexpected error fetching recommendations: {e}", exc_info=True)
        raise MovieRecommendationError("An unexpected error occurred. Please try again later.")


def fetch_movie_details(movie_id):
    """
    Fetch detailed information about a specific movie using its ID.
    
    :param movie_id: ID of the movie
    :return: Dictionary containing movie details
    """
    application_logger.info(f"Fetching details for movie ID: {movie_id}")
    url = f"{TMDB_API_URL}/movie/{movie_id}"
    params = {'api_key': TMDB_API_KEY}
    try:
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        movie_details = response.json()
        application_logger.info(f"Successfully fetched details for movie ID: {movie_id}.")
        return movie_details
    except requests.exceptions.HTTPError as e:
        error_logger.error(f"HTTPError fetching movie details for ID {movie_id}: {e}", exc_info=True)
        raise MovieRecommendationError("Could not fetch movie details. Please try again later.")
    except requests.exceptions.RequestException as e:
        error_logger.error(f"RequestException fetching movie details for ID {movie_id}: {e}", exc_info=True)
        raise MovieRecommendationError("An error occurred while fetching movie details. Please try again.")
    except Exception as e:
        error_logger.error(f"Unexpected error fetching movie details for ID {movie_id}: {e}", exc_info=True)
        raise MovieRecommendationError("An unexpected error occurred. Please try again later.")
