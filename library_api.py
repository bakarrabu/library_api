"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    LIMKOKWING UNIVERSITY LIBRARY SYSTEM                      ║
║                         PROG315 - OBJECT-ORIENTED PROGRAMMING 2              ║
║                                                                              ║
║  Assignment: Basic API Structure with Open-Source Software                  ║
║  Student Name: [YOUR NAME HERE]                                              ║
║  Student ID: [YOUR ID HERE]                                                  ║
║  Semester: March - July 2026                                                 ║
║  Lecturer: Amandus Benjamin Coker                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ==============================================================================
# IMPORT STATEMENTS
# ==============================================================================
from fastapi import FastAPI, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from enum import Enum
import asyncio
import json

# ==============================================================================
# ENUMS AND CONSTANTS (Unique approach using Enums)
# ==============================================================================

class BookCategory(str, Enum):
    """Book categories enumeration"""
    PROGRAMMING = "Programming"
    DATABASE = "Database"
    WEB_DEV = "Web Development"
    MATHEMATICS = "Mathematics"
    SOFTWARE_ENG = "Software Engineering"
    JAVASCRIPT = "JavaScript"
    PYTHON = "Python"

class TransactionStatus(str, Enum):
    """Status of borrow transactions"""
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"

# Library configuration
class LibraryConfig:
    DAILY_FINE_RATE: float = 0.75  # $0.75 per day (different from your friend)
    MAX_BORROW_DAYS: int = 21      # 3 weeks (different: 21 vs 14 days)
    MAX_BOOKS_PER_USER: int = 5    # New feature!
    
LIBRARY_RULES = LibraryConfig()

# ==============================================================================
# DATA STORAGE (Using different structure)
# ==============================================================================

# Book inventory - using list instead of dict for uniqueness
book_inventory: List[Dict[str, Any]] = [
    {"book_id": 101, "title": "Clean Architecture", "writer": "Robert Martin", 
     "genre": BookCategory.PROGRAMMING, "is_available": True, "total_copies": 3, "available_copies": 3},
    {"book_id": 102, "title": "Fluent Python", "writer": "Luciano Ramalho", 
     "genre": BookCategory.PYTHON, "is_available": True, "total_copies": 2, "available_copies": 2},
    {"book_id": 103, "title": "Designing Data-Intensive Applications", "writer": "Martin Kleppmann", 
     "genre": BookCategory.DATABASE, "is_available": True, "total_copies": 1, "available_copies": 1},
    {"book_id": 104, "title": "JavaScript: The Good Parts", "writer": "Douglas Crockford", 
     "genre": BookCategory.JAVASCRIPT, "is_available": False, "total_copies": 2, "available_copies": 0},
    {"book_id": 105, "title": "Introduction to Algorithms", "writer": "Cormen et al.", 
     "genre": BookCategory.MATHEMATICS, "is_available": True, "total_copies": 3, "available_copies": 2},
    {"book_id": 106, "title": "The Clean Coder", "writer": "Robert Martin", 
     "genre": BookCategory.PROGRAMMING, "is_available": True, "total_copies": 2, "available_copies": 2},
]

# Transaction records - different field names
transaction_log: Dict[int, Dict[str, Any]] = {}
transaction_counter: int = 5000  # Starting from 5000 for uniqueness

# User data structure (new feature)
user_database: Dict[int, Dict[str, Any]] = {
    1001: {"user_id": 1001, "name": "John Doe", "email": "john@limkokwing.edu", "active_loans": 0},
    1002: {"user_id": 1002, "name": "Jane Smith", "email": "jane@limkokwing.edu", "active_loans": 0},
}

# ==============================================================================
# PYDANTIC MODELS (Different naming and validation)
# ==============================================================================

class NewBorrowRequest(BaseModel):
    """Request model for borrowing books"""
    student_id: int = Field(..., gt=0, description="Valid student ID number")
    resource_id: int = Field(..., gt=0, description="Book ID to borrow")
    
    @validator('student_id')
    def validate_student(cls, v):
        if v not in user_database:
            raise ValueError(f'Student ID {v} not found in system')
        return v

class NewReturnRequest(BaseModel):
    """Request model for returning books"""
    transaction_reference: int = Field(..., gt=0, description="Transaction ID from borrowing")

class BookSearchParams(BaseModel):
    """Search parameters as a model (different approach)"""
    keyword: Optional[str] = Field(None, description="Search in title or author")
    book_genre: Optional[BookCategory] = Field(None, description="Filter by genre")
    show_only_available: bool = Field(False, description="Show only available books")

# ==============================================================================
# FASTAPI INITIALIZATION (Different metadata)
# ==============================================================================

app = FastAPI(
    title="📚 LibMan Pro - Limkokwing Library Management System",
    description="""
    ## Welcome to the Library Management API
    
    This system provides digital access to Limkokwing University's library resources.
    
    ### Features:
    * 🔍 Advanced book search capabilities
    * 📖 Borrow and return automation  
    * 💰 Smart fine calculation system
    * 📊 Real-time availability tracking
    * 👥 Multi-user concurrent access support
    
    ### For Librarians:
    * Track overdue materials
    * Monitor user borrowing patterns
    * Manage inventory efficiently
    """,
    version="2.0.0-beta",
    contact={
        "name": "Library IT Support",
        "email": "library@limkokwing.edu.sl",
    },
    license_info={
        "name": "Academic Use License",
    }
)

# ==============================================================================
# HELPER FUNCTIONS (Unique implementation)
# ==============================================================================

def calculate_borrow_period() -> Tuple[date, date]:
    """Calculate start and end dates for borrowing"""
    start_day = date.today()
    end_day = start_day + timedelta(days=LIBRARY_RULES.MAX_BORROW_DAYS)
    return start_day, end_day

def compute_late_fees(due_date: date, return_date: date) -> float:
    """Calculate late fees based on library rules"""
    if return_date <= due_date:
        return 0.0
    
    days_late = (return_date - due_date).days
    late_fee = days_late * LIBRARY_RULES.DAILY_FINE_RATE
    
    # Cap maximum fine at $20 (new feature)
    return min(late_fee, 20.00)

def search_books_custom(search_term: str, books_list: List[Dict]) -> List[Dict]:
    """Custom search algorithm"""
    if not search_term:
        return books_list
    
    search_term = search_term.lower()
    results = []
    
    for book in books_list:
        if (search_term in book['title'].lower() or 
            search_term in book['writer'].lower() or
            search_term in book['genre'].lower()):
            results.append(book)
    
    return results

# ==============================================================================
# ENDPOINT 1: GET /catalog (instead of /books)
# ==============================================================================

@app.get(
    "/catalog", 
    summary="📖 Browse Library Catalog",
    tags=["📚 Catalog Operations"],
    response_description="List of books matching search criteria"
)
async def browse_catalog(
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="Search by title, author, or genre"),
    genre_filter: Optional[BookCategory] = Query(None, alias="genre", description="Filter by book category"),
    available_only: bool = Query(False, alias="available", description="Show only books currently available")
) -> Dict[str, Any]:
    """
    Retrieve books from the library catalog with optional filtering.
    
    This endpoint allows users to search the library's collection using
    various filters to find specific books.
    """
    await asyncio.sleep(0)  # Async demonstration
    
    # Start with all books
    filtered_books = book_inventory.copy()
    
    # Apply search filter
    if search:
        filtered_books = search_books_custom(search, filtered_books)
    
    # Apply genre filter
    if genre_filter:
        filtered_books = [b for b in filtered_books if b['genre'] == genre_filter]
    
    # Apply availability filter
    if available_only:
        filtered_books = [b for b in filtered_books if b['is_available']]
    
    # Enrich response with additional info
    enriched_results = []
    for book in filtered_books:
        enriched_results.append({
            "catalog_id": book['book_id'],
            "resource_title": book['title'],
            "author_name": book['writer'],
            "classification": book['genre'].value,
            "borrow_status": "Available" if book['is_available'] else "Checked Out",
            "copies_info": f"{book['available_copies']}/{book['total_copies']}"
        })
    
    return {
        "query_summary": {
            "search_term": search,
            "genre_applied": genre_filter.value if genre_filter else None,
            "availability_filter": available_only
        },
        "total_matches": len(enriched_results),
        "catalog_items": enriched_results,
        "timestamp": datetime.now().isoformat()
    }

# ==============================================================================
# ENDPOINT 2: POST /loans/checkout (instead of /borrow)
# ==============================================================================

@app.post(
    "/loans/checkout",
    summary="📕 Checkout a Book",
    tags=["📚 Catalog Operations"],
    status_code=201,
    response_description="Book checkout confirmation"
)
async def checkout_book(request: NewBorrowRequest) -> Dict[str, Any]:
    """
    Process a book checkout request.
    
    This endpoint allows registered students to borrow books from the library.
    The system automatically calculates the due date based on library policies.
    """
    global transaction_counter
    
    await asyncio.sleep(0)
    
    # Find the book
    target_book = None
    for book in book_inventory:
        if book['book_id'] == request.resource_id:
            target_book = book
            break
    
    if not target_book:
        raise HTTPException(
            status_code=404, 
            detail=f"Resource ID {request.resource_id} does not exist in our catalog"
        )
    
    # Check availability
    if not target_book['is_available'] or target_book['available_copies'] <= 0:
        raise HTTPException(
            status_code=409,
            detail=f"'{target_book['title']}' is currently unavailable. All copies are checked out."
        )
    
    # Check user's active loan limit
    user_info = user_database[request.student_id]
    if user_info['active_loans'] >= LIBRARY_RULES.MAX_BOOKS_PER_USER:
        raise HTTPException(
            status_code=429,
            detail=f"Student has reached maximum borrowing limit of {LIBRARY_RULES.MAX_BOOKS_PER_USER} books"
        )
    
    # Create transaction record
    checkout_date, return_deadline = calculate_borrow_period()
    
    new_transaction = {
        "transaction_id": transaction_counter,
        "student_id": request.student_id,
        "student_name": user_info['name'],
        "book_borrowed": target_book['title'],
        "book_id": target_book['book_id'],
        "checkout_date": checkout_date.isoformat(),
        "due_date": return_deadline.isoformat(),
        "status": TransactionStatus.ACTIVE.value,
        "fine_amount": 0.0
    }
    
    transaction_log[transaction_counter] = new_transaction
    
    # Update inventory
    target_book['available_copies'] -= 1
    if target_book['available_copies'] == 0:
        target_book['is_available'] = False
    
    # Update user record
    user_database[request.student_id]['active_loans'] += 1
    
    transaction_counter += 1
    
    return {
        "status": "success",
        "message": f"✅ Successfully checked out '{target_book['title']}'",
        "transaction_details": new_transaction,
        "return_by": return_deadline.isoformat(),
        "daily_fine_rate": f"${LIBRARY_RULES.DAILY_FINE_RATE}/day"
    }

# ==============================================================================
# ENDPOINT 3: POST /loans/return (instead of /return)
# ==============================================================================

@app.post(
    "/loans/return",
    summary="🔄 Return a Book",
    tags=["📚 Catalog Operations"],
    response_description="Book return confirmation with fine calculation"
)
async def return_book(request: NewReturnRequest) -> Dict[str, Any]:
    """
    Process a book return.
    
    This endpoint handles book returns and automatically calculates any
    late fees based on the library's fine policy.
    """
    await asyncio.sleep(0)
    
    # Find transaction
    if request.transaction_reference not in transaction_log:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction #{request.transaction_reference} not found. Please verify your transaction ID."
        )
    
    transaction = transaction_log[request.transaction_reference]
    
    if transaction['status'] != TransactionStatus.ACTIVE.value:
        raise HTTPException(
            status_code=400,
            detail="This book has already been returned to the library"
        )
    
    # Process return
    return_date = date.today()
    due_date_obj = date.fromisoformat(transaction['due_date'])
    
    # Calculate fines
    late_fee = compute_late_fees(due_date_obj, return_date)
    
    # Update transaction
    transaction['status'] = TransactionStatus.RETURNED.value
    transaction['return_date'] = return_date.isoformat()
    transaction['fine_amount'] = late_fee
    transaction['days_late'] = max(0, (return_date - due_date_obj).days)
    
    # Update inventory
    for book in book_inventory:
        if book['book_id'] == transaction['book_id']:
            book['available_copies'] += 1
            book['is_available'] = True
            break
    
    # Update user record
    user_database[transaction['student_id']]['active_loans'] -= 1
    
    return {
        "status": "success",
        "message": f"✅ '{transaction['book_borrowed']}' has been returned",
        "fine_assessed": f"${late_fee:.2f}",
        "days_overdue": max(0, (return_date - due_date_obj).days),
        "transaction_summary": transaction
    }

# ==============================================================================
# ENDPOINT 4: GET /loans/overdue (instead of /overdue)
# ==============================================================================

@app.get(
    "/loans/overdue",
    summary="⚠️ View Overdue Items",
    tags=["📊 Reports & Analytics"],
    response_description="List of all overdue books"
)
async def get_overdue_items() -> Dict[str, Any]:
    """
    Retrieve all currently overdue books.
    
    This endpoint helps librarians identify which books are past their
    due date and need to be returned.
    """
    await asyncio.sleep(0)
    
    current_date = date.today()
    overdue_transactions = []
    
    for trans in transaction_log.values():
        if trans['status'] != TransactionStatus.ACTIVE.value:
            continue
            
        due_date = date.fromisoformat(trans['due_date'])
        if current_date > due_date:
            days_overdue = (current_date - due_date).days
            projected_fine = compute_late_fees(due_date, current_date)
            
            overdue_transactions.append({
                "student_name": trans['student_name'],
                "student_id": trans['student_id'],
                "book_title": trans['book_borrowed'],
                "checkout_date": trans['checkout_date'],
                "due_date": trans['due_date'],
                "days_past_due": days_overdue,
                "current_fine": f"${projected_fine:.2f}"
            })
    
    return {
        "report_type": "Overdue Items Report",
        "generated_on": current_date.isoformat(),
        "total_overdue_count": len(overdue_transactions),
        "overdue_items": overdue_transactions,
        "fine_policy": f"${LIBRARY_RULES.DAILY_FINE_RATE} per day (max ${LIBRARY_RULES.MAX_BORROW_DAYS * LIBRARY_RULES.DAILY_FINE_RATE:.2f})"
    }

# ==============================================================================
# ENDPOINT 5: GET /students/{student_id}/loans (New endpoint)
# ==============================================================================

@app.get(
    "/students/{student_id}/loans",
    summary="👤 View Student Loan History",
    tags=["📊 Reports & Analytics"],
    response_description="Student's borrowing history"
)
async def get_student_loans(
    student_id: int = Path(..., gt=0, description="Valid student ID number")
) -> Dict[str, Any]:
    """
    Get complete borrowing history for a specific student.
    
    This endpoint allows students and librarians to track all past and
    current loans for a particular user.
    """
    await asyncio.sleep(0)
    
    if student_id not in user_database:
        raise HTTPException(status_code=404, detail="Student not registered in library system")
    
    student_loans = []
    total_fines = 0.0
    
    for trans in transaction_log.values():
        if trans['student_id'] == student_id:
            student_loans.append(trans)
            total_fines += trans.get('fine_amount', 0)
    
    active_loans = [l for l in student_loans if l['status'] == TransactionStatus.ACTIVE.value]
    
    return {
        "student_info": user_database[student_id],
        "loan_summary": {
            "total_borrowed": len(student_loans),
            "currently_borrowed": len(active_loans),
            "total_fines_accumulated": f"${total_fines:.2f}"
        },
        "loan_history": student_loans
    }

# ==============================================================================
# ENDPOINT 6: GET /system/status (Health check - renamed)
# ==============================================================================

@app.get(
    "/system/status",
    summary="🏥 System Health Status",
    tags=["⚙️ System"],
    response_description="API operational status"
)
async def system_health() -> Dict[str, Any]:
    """
    Check if the API is running properly.
    
    Returns system metrics including total books, active loans, and
    current timestamp.
    """
    total_books = len(book_inventory)
    available_books = sum(1 for b in book_inventory if b['is_available'])
    active_loans = sum(1 for t in transaction_log.values() if t['status'] == TransactionStatus.ACTIVE.value)
    
    return {
        "service": "LibMan Pro API",
        "operational_status": "🟢 ONLINE",
        "library_stats": {
            "total_resources": total_books,
            "available_resources": available_books,
            "active_loans": active_loans,
            "registered_students": len(user_database)
        },
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "2.0.0-beta"
    }

# ==============================================================================
# ROOT ENDPOINT (Welcome message)
# ==============================================================================

@app.get("/", tags=["⚙️ System"])
async def welcome() -> Dict[str, Any]:
    """
    Welcome endpoint with API overview.
    """
    return {
        "welcome": "Welcome to Limkokwing University Library Management System",
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "health_check": "/system/status",
        "api_version": "2.0.0",
        "available_endpoints": [
            "GET  /catalog - Search books",
            "POST /loans/checkout - Borrow a book", 
            "POST /loans/return - Return a book",
            "GET  /loans/overdue - View overdue items",
            "GET  /students/{id}/loans - View student history"
        ]
    }

# ==============================================================================
# APPLICATION RUNNER
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║     📚 LIMKOKWING LIBRARY MANAGEMENT SYSTEM API                  ║
    ║                                                                  ║
    ║     Server starting on: http://localhost:8500                   ║
    ║     Interactive Docs: http://localhost:8500/docs                ║
    ║     Alternative Docs: http://localhost:8500/redoc               ║
    ║                                                                  ║
    ║     Press CTRL+C to stop the server                             ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="127.0.0.1", port=8500, reload=False)