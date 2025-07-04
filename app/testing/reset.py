"""
Database reset functionality for testing
Restores the database to its original seed state
"""

import sqlite3
import subprocess
import os
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import engine, SessionLocal
from app.models import ListingItem


def reset_database() -> dict:
    """
    Reset the database to its original seed state
    Returns status and message
    """
    try:
        # Close all existing connections
        engine.dispose()

        # Get database path
        db_path = "listings.db"

        # Remove existing database file if it exists
        if os.path.exists(db_path):
            os.remove(db_path)

        # Recreate database tables
        from app.database import Base

        Base.metadata.create_all(bind=engine)

        # Run the seed data script
        result = subprocess.run(["python", "combined_seed_data.py"], capture_output=True, text=True, cwd=".")

        if result.returncode != 0:
            return {
                "success": False,
                "message": f"Failed to run seed script: {result.stderr}",
                "details": result.stdout,
            }

        # Verify the reset by counting records
        db = SessionLocal()
        try:
            total_count = db.query(ListingItem).count()
            active_count = db.query(ListingItem).filter(ListingItem.status == "ACTIVE").count()
            inactive_count = db.query(ListingItem).filter(ListingItem.status == "INACTIVE").count()

            return {
                "success": True,
                "message": "Database reset successfully",
                "details": {
                    "total_listings": total_count,
                    "active_listings": active_count,
                    "inactive_listings": inactive_count,
                    "seed_script_output": result.stdout,
                },
            }
        finally:
            db.close()

    except Exception as e:
        return {"success": False, "message": f"Error resetting database: {str(e)}", "details": None}


def get_database_state() -> dict:
    """
    Get current database state for comparison
    Returns summary statistics and key data points
    """
    try:
        db = SessionLocal()
        try:
            # Basic counts
            total_count = db.query(ListingItem).count()
            active_count = db.query(ListingItem).filter(ListingItem.status == "ACTIVE").count()
            inactive_count = db.query(ListingItem).filter(ListingItem.status == "INACTIVE").count()

            # Count by seller
            seller_counts = {}
            sellers = db.query(ListingItem.seller_id, ListingItem.seller_name).distinct().all()
            for seller_id, seller_name in sellers:
                count = db.query(ListingItem).filter(ListingItem.seller_id == seller_id).count()
                seller_counts[seller_id] = {"name": seller_name, "count": count}

            # Price statistics
            price_stats = db.query(
                func.min(ListingItem.price), func.max(ListingItem.price), func.avg(ListingItem.price)
            ).first()

            # Total inventory
            total_quantity = db.query(func.sum(ListingItem.quantity)).scalar() or 0

            return {
                "success": True,
                "state": {
                    "total_listings": total_count,
                    "active_listings": active_count,
                    "inactive_listings": inactive_count,
                    "seller_counts": seller_counts,
                    "price_stats": {
                        "min_price": float(price_stats[0]) if price_stats[0] else 0,
                        "max_price": float(price_stats[1]) if price_stats[1] else 0,
                        "avg_price": float(price_stats[2]) if price_stats[2] else 0,
                    },
                    "total_inventory": total_quantity,
                },
            }
        finally:
            db.close()

    except Exception as e:
        return {"success": False, "message": f"Error getting database state: {str(e)}", "state": None}


def backup_current_state() -> dict:
    """
    Create a backup of current database state
    Returns backup information
    """
    try:
        import shutil
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"listings_backup_{timestamp}.db"

        shutil.copy2("listings.db", backup_path)

        return {
            "success": True,
            "message": "Database backed up successfully",
            "backup_path": backup_path,
            "timestamp": timestamp,
        }

    except Exception as e:
        return {"success": False, "message": f"Error backing up database: {str(e)}", "backup_path": None}
