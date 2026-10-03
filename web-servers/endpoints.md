# URL Shortener Endpoints

This document outlines the API endpoints available in the URL shortener application (`app.py`).

## `GET /`

- **Description**: Health check endpoint to verify the service is running.
- **Response**: `200 OK` with text `"URL Shortener is running!\n"`

## `POST /shorten`

- **Description**: Accepts a URL and generates a short code for it. If the URL already exists in the database, it returns the existing short code.
- **Request Format**: Form Data (`application/x-www-form-urlencoded`)
- **Parameters**:
  - `url` (string): The original URL to be shortened.
- **Response**: `200 OK`
  - **Body**: JSON object containing the shortened URL path.
    ```json
    {
      "short_url": "/<short_code>"
    }
    ```

## `GET /<short_code>`

- **Description**: Redirects the user to the original URL associated with the provided short code.
- **Parameters**: 
  - `short_code` (string): The 6-character short code in the URL path.
- **Response**: 
  - `302 Found`: Redirects to the original URL if found.
  - `404 Not Found`: Returns `"URL not found"` if the short code does not exist in the database.

## Rate Limiting

All endpoints are subject to rate limiting:
- **Limit**: 10 requests per 60 seconds per IP address.
- **Response on Exceeding Limit**: `429 Too Many Requests`
  - **Body**: 
    ```json
    {
      "error": "Rate limit exceeded"
    }
    ```
