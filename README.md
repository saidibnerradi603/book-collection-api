# Book Collection API

A RESTful API built with FastAPI and MongoDB for managing a collection of books with categories.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [API Endpoints](#api-endpoints)
  - [Books](#books)
  - [Categories](#categories)
- [Data Model](#data-model)
- [Setup and Installation](#setup-and-installation)
- [Environment Configuration](#environment-configuration)
- [Running the API](#running-the-api)
- [API Documentation](#api-documentation)
- [Example Usage](#example-usage)

## Overview

The Book Collection API provides a comprehensive set of endpoints to manage a collection of books. It allows users to create, read, update, and delete books, as well as search for books by various criteria. The API also provides endpoints for managing book categories.

## Features

- CRUD operations for books
- Sorting and filtering of book lists
- Searching books by title or author
- Book categorization
- Category statistics

## Tech Stack

- **FastAPI**: Modern, high-performance web framework for building APIs
- **MongoDB**: NoSQL database for storing book data
- **PyMongo**: Python driver for MongoDB
- **Pydantic**: Data validation 
- **Python-dotenv**: Environment variable management

## API Endpoints

### Books

- **GET /** - Root endpoint
  - Returns a welcome message

- **POST /books** - Create a new book
  - Request body: Book object with title, author, year, rating, and categories
  - Returns the created book with its ID

- **GET /books** - List all books
  - Query parameters:
    - `sort_by`: Sort by "year" or "rating"
    - `order`: Sort in "asc" or "desc" order
  - Returns a list of all books

- **GET /books/{book_id}** - Get a specific book
  - Path parameter: `book_id` - MongoDB ObjectId of the book
  - Returns the book with the specified ID

- **PUT /books/{book_id}** - Update a book
  - Path parameter: `book_id` - MongoDB ObjectId of the book
  - Request body: BookUpdate object with fields to update
  - Returns the updated book

- **DELETE /books/{book_id}** - Delete a book
  - Path parameter: `book_id` - MongoDB ObjectId of the book
  - Returns a confirmation message and the deleted book ID

- **GET /books/search/** - Search books
  - Query parameters:
    - `title` (optional): Partial title match
    - `author` (optional): Partial author match
  - Returns books matching the search criteria

### Categories

- **GET /categories** - List all unique categories
  - Returns a list of all unique categories across all books

- **GET /books/categories/stats** - Get category statistics
  - Returns the count of books for each category

## Data Model

### Book Schema

```json
{
  "title": "string",
  "author": "string",
  "year": "integer",
  "rating": "float",
  "categories": ["string"]
}
```

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account or local MongoDB instance

### Installation Steps

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv fastapi_env
   ```
3. Activate the virtual environment:
   - Windows:
     ```bash
     fastapi_env\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source fastapi_env/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt 
   ```

## Environment Configuration

Create a `.env` file in the project root with your MongoDB connection string. You can copy the provided `.env.example` file as a starting point:

```bash
# On Windows
copy .env.example .env

# On macOS/Linux
cp .env.example .env
```

Then modify the `.env` file with your actual MongoDB connection string

## Running the API

Start the FastAPI server with Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000.

## API Documentation

FastAPI automatically generates API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Example Usage

### Creating a Book

```bash
curl -X 'POST' \
  'http://localhost:8000/books' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Mathematics for Machine Learning",
  "author": "Marc Peter Deisenroth, A. Aldo Faisal, Cheng Soon Ong",
  "year": 2020,
  "rating": 4.5,
  "categories": [
    "Mathematical Foundations",
    "Machine Learning Algorithms"
  ]
}'

```

### Getting Category Statistics

```bash
curl -X 'GET' \
  'http://localhost:8000/books/categories/stats' \
  -H 'accept: application/json'
```

