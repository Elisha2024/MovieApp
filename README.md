# MovieApp

MovieApp is a Django-based application that leverages the TMDb API to provide movie recommendations, detailed information, and user ratings. It implements caching, logging, and user-friendly API endpoints for a seamless experience.

---

## Features

1. **Movie Recommendations**  
   - **Endpoint:** `POST /api/recommendations/`  
   - **Request Body:**  
     ```json
     {
       "genres": [35, 18],
       "language": "en",
       "release_year": 1980
     }
     ```
   - Fetches recommended movies from TMDb API based on user preferences (genres, language, release year).  
   - **Response Example:**
     ```json
     {
       "results": [
         {
           "id": 1,
           "title": "Movie Title",
           "overview": "Movie description",
           "release_date": "1980-05-30",
           "vote_average": 8.5
         }
       ]
     }
     ```

2. **Movie Details**  
   - **Endpoint:** `GET /api/movie/<movie_id>/`  
   - Fetches detailed information about a movie using its ID.  
   - **Response Example:**
     ```json
     {
       "id": 1,
       "title": "Movie Title",
       "overview": "Movie description",
       "release_date": "1980-05-30",
       "runtime": 120,
       "genres": ["Comedy", "Drama"]
     }
     ```

3. **Movie Ratings**  
   - **Endpoint:** `POST /api/ratings/`  
   - **Request Body:**  
     ```json
     {
       "movie_id": 18,
       "rating": 2.5
     }
     ```
   - Saves user ratings for specific movies locally.

4. **Caching with Redis**  
   - Caches movie recommendations for specific user preferences (10-minute duration).  
   - Caches detailed movie information to reduce redundant API calls.

5. **Logging**  
   - Logs API requests, cache hits/misses, and errors.  
   - Logs are stored for later review and debugging.

6. **Additional Features**  
   - Input validation for invalid genres or movie IDs.  
   - Graceful handling of TMDb API rate limits or failures.  
   - Modular code for API calls, caching, and database operations.  
   - User authentication to personalize movie recommendations.  
   - "Trending Movies" endpoint to fetch the latest popular movies from TMDb.  
   - Pagination for movie recommendations.

---

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/Elisha2024/MovieApp.git
   cd movieapp

2. python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

3. Configure your environment variables:

Create a .env file in the root directory with the following content:
TMDB_API_KEY=your_tmdb_api_key
DEBUG=True

Add Redis credentials to your environment

4. Run migrations:
python manage.py migrate


Start the development server:
python manage.py runserver