# Limkokwing Library API

**PROG315 — Object-Oriented Programming 2**
Individual Assignment | Semester 04 | March–July 2026

## Description
A RESTful API for the Limkokwing University Digital Library built with Python FastAPI. Supports book search, borrowing, returning, overdue tracking, and concurrent multi-user access via async/await.

## Tech Stack
- Python 3.12
- FastAPI
- Pydantic v2
- asyncio
- Uvicorn (ASGI server)

## Setup
```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

## Endpoints
| Method | Endpoint        | Description              |
|--------|-----------------|--------------------------|
| GET    | /books          | Search books by filter   |
| POST   | /borrow         | Borrow a book            |
| POST   | /return         | Return a book + fine     |
| GET    | /overdue        | List overdue books       |
| GET    | /books/{id}     | Get book by ID           |

## Run Simulation (no server needed)
```bash
python3 simulation.py
```

## SDG Alignment
**SDG 4 — Quality Education**: This API removes barriers to library access by making resources available digitally at any time.

## Examiner
Amandus Benjamin Coker — amandus.bcoker@limkokwing.edu.sl
