"""
Limkokwing University Library API — Async Simulation Script
PROG315 Object-Oriented Programming 2
Demonstrates async/await with type annotations (no server needed)
"""

import asyncio
from datetime import date, timedelta
from typing import Optional

# ─── In-Memory Data Store ─────────────────────────────────────────────────────
books_db: dict[int, dict] = {
    1: {"id": 1, "title": "Clean Code",               "author": "Robert C. Martin", "category": "Programming",         "available": True},
    2: {"id": 2, "title": "The Pragmatic Programmer",  "author": "David Thomas",     "category": "Programming",         "available": True},
    3: {"id": 3, "title": "Introduction to Algorithms","author": "Thomas H. Cormen", "category": "Mathematics",         "available": True},
    4: {"id": 4, "title": "Design Patterns",           "author": "Gang of Four",     "category": "Software Engineering","available": False},
    5: {"id": 5, "title": "Python Crash Course",       "author": "Eric Matthes",     "category": "Programming",         "available": True},
}

borrow_records: dict[int, dict] = {}
_borrow_id_counter: int = 1
FINE_PER_DAY: float = 0.50


# ─── Endpoint Simulations ─────────────────────────────────────────────────────

async def search_books(
    title: Optional[str] = None,
    author: Optional[str] = None,
    category: Optional[str] = None
) -> dict:
    """GET /books — Search books by title, author, or category."""
    await asyncio.sleep(0.05)
    results = list(books_db.values())
    if title:
        results = [b for b in results if title.lower() in b["title"].lower()]
    if author:
        results = [b for b in results if author.lower() in b["author"].lower()]
    if category:
        results = [b for b in results if category.lower() in b["category"].lower()]
    return {"count": len(results), "books": results}


async def borrow_book(user_id: int, book_id: int) -> dict:
    """POST /borrow — Borrow a book; sets 14-day due date."""
    global _borrow_id_counter
    await asyncio.sleep(0.05)
    book = books_db.get(book_id)
    if not book:
        return {"error": f"Book ID {book_id} not found."}
    if not book["available"]:
        return {"error": f"'{book['title']}' is not available."}

    borrow_date: date = date.today()
    due_date: date = borrow_date + timedelta(days=14)
    record: dict = {
        "borrow_id": _borrow_id_counter,
        "user_id": user_id,
        "book_id": book_id,
        "borrow_date": str(borrow_date),
        "due_date": str(due_date),
        "returned": False,
        "fine": 0.0
    }
    borrow_records[_borrow_id_counter] = record
    books_db[book_id]["available"] = False
    _borrow_id_counter += 1
    return {"message": f"'{book['title']}' borrowed successfully.", "record": record}


async def return_book(borrow_id: int) -> dict:
    """POST /return — Return a book and compute any overdue fine."""
    await asyncio.sleep(0.05)
    record = borrow_records.get(borrow_id)
    if not record:
        return {"error": f"Borrow record {borrow_id} not found."}
    if record["returned"]:
        return {"error": "Book already returned."}

    due: date = date.fromisoformat(record["due_date"])
    today: date = date.today()
    fine: float = 0.0
    if today > due:
        fine = round((today - due).days * FINE_PER_DAY, 2)

    record["returned"] = True
    record["fine"] = fine
    books_db[record["book_id"]]["available"] = True
    book_title: str = books_db[record["book_id"]]["title"]
    return {"message": f"'{book_title}' returned.", "fine_charged": fine, "record": record}


async def get_overdue_books() -> dict:
    """GET /overdue — List unreturned books past due date with fines."""
    await asyncio.sleep(0.05)
    today: date = date.today()
    overdue: list[dict] = []
    for record in borrow_records.values():
        if record["returned"]:
            continue
        due: date = date.fromisoformat(record["due_date"])
        if today > due:
            overdue_days: int = (today - due).days
            overdue.append({
                **record,
                "book_title": books_db[record["book_id"]]["title"],
                "overdue_days": overdue_days,
                "current_fine": round(overdue_days * FINE_PER_DAY, 2)
            })
    return {"total_overdue": len(overdue), "overdue_books": overdue}


async def get_book_by_id(book_id: int) -> dict:
    """GET /books/{book_id} — Retrieve one book's details."""
    await asyncio.sleep(0.05)
    book = books_db.get(book_id)
    if not book:
        return {"error": f"Book ID {book_id} not found."}
    return book


# ─── Demo Runner ──────────────────────────────────────────────────────────────

def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


async def main() -> None:
    section("DEMO 1 — Search for Programming books")
    result = await search_books(category="Programming")
    print(f"  Found {result['count']} books:")
    for b in result["books"]:
        status = "Available" if b["available"] else "Unavailable"
        print(f"    [{b['id']}] {b['title']} by {b['author']} — {status}")

    section("DEMO 2 — Borrow a specific book (Book ID 1)")
    result = await borrow_book(user_id=101, book_id=1)
    print(f"  {result.get('message', result.get('error'))}")
    borrow_id_101 = result.get("record", {}).get("borrow_id")
    if borrow_id_101:
        print(f"  Borrow ID: {borrow_id_101}  |  Due: {result['record']['due_date']}")

    section("DEMO 3 — Return the borrowed book")
    result = await return_book(borrow_id=borrow_id_101)
    print(f"  {result.get('message', result.get('error'))}")
    print(f"  Fine Charged: ${result.get('fine_charged', 0):.2f}")

    section("DEMO 4 — Get book details by ID")
    result = await get_book_by_id(book_id=3)
    print(f"  Title   : {result.get('title')}")
    print(f"  Author  : {result.get('author')}")
    print(f"  Category: {result.get('category')}")
    print(f"  Status  : {'Available' if result.get('available') else 'Unavailable'}")

    section("DEMO 5 — Overdue Books (injecting old record)")
    # Inject an overdue record manually for demonstration
    borrow_records[555] = {
        "borrow_id": 555, "user_id": 200, "book_id": 5,
        "borrow_date": "2026-03-01", "due_date": "2026-03-15",
        "returned": False, "fine": 0.0
    }
    books_db[5]["available"] = False
    result = await get_overdue_books()
    print(f"  Total Overdue: {result['total_overdue']}")
    for item in result["overdue_books"]:
        print(f"    Book: {item['book_title']}  |  Overdue: {item['overdue_days']} days  |  Fine: ${item['current_fine']:.2f}")

    section("DEMO 6 — Concurrent Borrow Requests (Async/Await)")
    # Reset
    books_db[2]["available"] = True
    books_db[3]["available"] = True

    tasks = [
        borrow_book(user_id=201, book_id=2),
        borrow_book(user_id=202, book_id=2),   # Same book — conflict
        borrow_book(user_id=203, book_id=3),
    ]
    print("  Launching 3 concurrent borrow requests via asyncio.gather()...")
    results = await asyncio.gather(*tasks)
    for r in results:
        msg = r.get("message") or r.get("error")
        uid = r.get("record", {}).get("user_id", "?")
        print(f"    User {uid}: {msg}")

    section("SIMULATION COMPLETE")
    print("  All endpoints tested successfully.\n")


if __name__ == "__main__":
    asyncio.run(main())
