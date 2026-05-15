from fastapi import FastAPI,Body, HTTPException,Query,Path
from db_connector import get_database_connection
from typing import List,Optional
from pydantic import  BaseModel,Field,field_validator
from datetime import datetime
from bson import ObjectId




app=FastAPI(
    title="Book Collection API",
    description="A RESTful API for managing books and categories.It allows you to create, read, update, delete, and search books, as well as view category information and statistics.",
    docs_url="/docs",
    redoc_url="/redoc",
)

    
# Connect to Mongodb 
books =get_database_connection(db_name="books")

# Access the "book_collection" collection
book_collection=books["book_collection"]

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., gt=0, lt=datetime.now().year + 1)
    rating: float = Field(..., ge=0, le=5)
    categories: List[str] = Field(default=[])
    
    # Validate Rating 
    @field_validator('rating')
    def validate_rating_decimal(cls, v):
        if round(v * 10) != v * 10:
            raise ValueError('Rating must have at most 1 decimal place')
        return v
    
class BookUpdate(BaseModel):
    title: Optional[str]  = Field(default=None, min_length=1, max_length=100)
    author: Optional[str] = Field(default=None, min_length=1, max_length=100)
    year: Optional[int]   = Field(default=None, gt=0, lt=datetime.now().year + 1)
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    categories: Optional[List[str]] = Field(default_factory=list)
    
    # Validate Rating 
    @field_validator('rating')
    def validate_rating_decimal(cls, v):
        if round(v * 10) != v * 10:
            raise ValueError('Rating must have at most 1 decimal place')
        return v
    
class BookResponse(BaseModel):
    id: str = Field(alias="_id") 
    title: str
    author: str
    year: int
    rating: float
    categories: List[str]
    
    

    @field_validator("id", mode="before")
    @classmethod
    def validate_object_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return str(v)




# GET / – Root endpoint.
@app.get("/",tags=["Home"])
def root():
   return {"message": "Welcome to the API!"}



# POST /books – Create a new book.
@app.post("/books", status_code=201, tags=["Books"], 
         summary="Create a new book", response_description="The created book")
def create_new_book(book:BookCreate=Body(...)):
    book_dict=book.model_dump()
    result=book_collection.insert_one(book_dict)
    
    if result.acknowledged:
        book_dict["_id"] = str(result.inserted_id)
        return book_dict 
    else:
        raise HTTPException(status_code=500, detail="Failed to create book")

# GET /books – List all books.    
@app.get("/books",response_model=List[BookResponse],status_code=200,response_description="Get a list of all books",tags=["Books"])
def list_books(sort_by:str=Query(...,description="sort on the basis of  year or rating ",example="year"),
                     order:str=Query(...,description="Sort in ascending (asc) or descending (desc) order",example="asc"),
                     skip:int=Query(0, ge=0, description="Number of books to skip", example=0),
                     limit:int=Query(10, ge=1, description="Maximum number of books to return", example=10)):
    
    
    sort_by_values=["year","rating"]
    order_by_values=["asc","desc"]
    if sort_by not in sort_by_values:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by value. Must be one of: {sort_by_values}"
        )
    if order not in order_by_values:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid order value. Must be one of: {order_by_values}"
        )
       
        
    try:
        sort_direction=1 if order=="asc" else -1
        sort_params=None
        if sort_by:
            sort_params=[(sort_by, sort_direction)]
        results = book_collection.find()
        if sort_params:
            results = results.sort(sort_params)
        results = results.skip(skip).limit(limit)
        books=list(results) 
        return books
    except  Exception as e:
          raise HTTPException (
            status_code=500,
            detail=f"Failed to fetch books: {str(e)}"
        )
           
# GET /books/{book_id} – Retrieve a book by its ID.
@app.get("/books/{book_id}",response_model=BookResponse,status_code=200,response_description="Get a single book by its ID",tags=["Books"])
def get_book_by_id(book_id:str=Path(...,description="The MongoDB ObjectId of the book",example="689e1fb16253bf5c45c31d1c")):
    
    if not ObjectId.is_valid(book_id):
            raise HTTPException(detail="invalid id format",status_code=400)
    try:
        book=book_collection.find_one({"_id":ObjectId(book_id)})
    except Exception as e :
        raise HTTPException(status_code=500, detail=f"Failed to fetch book: {str(e)}")
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return book


# GET /books/search/ – Search books by title or author.
@app.get("/books/search/", response_model=List[BookResponse], tags=["Books"],
         summary="Search books by title or author", response_description="List of books matching search criteria")
def search_books(title: Optional[str] = Query(None, description="Search by title (partial match)", example="Programming"),author: Optional[str] = Query(None, description="Search by author (partial match)", example="Peter")):
    if not title and not author:
        raise HTTPException(status_code=400, detail="At least one search parameter (title or author) is required")
    
    search_query = {}
    
    if title:
        search_query["title"] = {"$regex": title, "$options": "i"}
    
    if author:
        search_query["author"] = {"$regex": author, "$options": "i"}
    
    try:
        results = book_collection.find(search_query)
        books = list(results)
        
        if not books:
            return []
        
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search books: {str(e)}")
    




# PUT /books/{book_id} – Update an existing book.
@app.put("/books/{book_id}", status_code=200, response_model=BookResponse, tags=["Books"], 
         summary="Update a book", response_description="The updated book")
def update_book_by_id(book_id: str = Path(..., description="The MongoDB ObjectId of the book", example="689e1fb16253bf5c45c31d1c"),
                     book_update: BookUpdate = Body(..., description="Any subset of fields to update")):
    
    if not ObjectId.is_valid(book_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    update_data = {k: v for k, v in book_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update data provided")
    
    try:
        result = book_collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Book not found")
        
        
        updated_book = book_collection.find_one({"_id": ObjectId(book_id)})
        return updated_book
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update book: {str(e)}")
    
# DELETE /books/{book_id} – Delete a book.
@app.delete("/books/{book_id}",status_code=200,summary="Delete a book",description="Delete a book by its ID",response_description="A message confirming deletion with the deleted book's ID",tags=["Books"])
def delete_book_by_id(book_id: str = Path(..., description="The MongoDB ObjectId of the book", example="689e1fb16253bf5c45c31d1c")):
    
    if not ObjectId.is_valid(book_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    result=book_collection.delete_one({"_id":ObjectId(book_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
        
    if result.deleted_count == 1:
        return {"message": "Book deleted successfully","deletedBookId": book_id}

# GET /categories – List all categories.
@app.get("/categories",status_code=200,response_model=list[str],description="List all unique categories across all books",response_description="A Lsit of  all unique categories across all books",tags=["Categories"])
def list_categories():
    categories_list=[]
    try:
        categories = book_collection.find({},{"categories": 1, "_id": 0})
        if not categories:
            return []
        for categorie in categories:
            for k in categorie["categories"]:
                categories_list.append(k)
        return list(set(categories_list))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search categories: {str(e)}")
        
        
# GET /books/categories/stats – Get category statistics.
@app.get("/books/categories/stats", status_code=200,
         summary="Get category statistics", response_description="Count of books per category",tags=["Categories"])
def get_category_stats():
    try:
        pipeline = [
            {"$unwind": "$categories"},
            {"$group": {"_id": "$categories", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        results = book_collection.aggregate(pipeline)
        stats = [{"category": item["_id"], "count": item["count"]} for item in results]
        
        return {"categories": stats}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category statistics: {str(e)}")
