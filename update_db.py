from app import app, db

with app.app_context():
    try:
        db.session.execute(
            db.text(
                "ALTER TABLE bug ADD COLUMN bug_source TEXT DEFAULT 'Testing Team'"
            )
        )
        print("bug_source column added")
    except Exception as e:
        print("bug_source:", e)

    try:
        db.session.execute(
            db.text(
                "ALTER TABLE bug ADD COLUMN created_by_id INTEGER"
            )
        )
        print("created_by_id column added")
    except Exception as e:
        print("created_by_id:", e)

    db.session.commit()

print("Database updated successfully")