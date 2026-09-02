from connection import db

collections = [
    "users",
    "workspaces",
    "documents",
    "financial_metrics",
    "red_flags",
    "comparisons",
    "chat_sessions",
    "messages",
    "reports"
]

for collection in collections:
    try:
        db.create_collection(collection)
        print(f"{collection} created")
    except Exception:
        print(f"{collection} already exists")

print("Database initialized successfully!")