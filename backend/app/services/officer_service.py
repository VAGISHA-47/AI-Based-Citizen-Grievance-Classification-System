"""Placeholder officer service helpers for the v1 scaffold."""

import logging

logger = logging.getLogger(__name__)

# Static mapping of complaint categories to assigned officer IDs
DEPT_OFFICERS = {
    "Water Supply": ["officer_w1", "officer_w2", "officer_w3"],
    "Roads": ["officer_r1", "officer_r2"],
    "Electricity": ["officer_e1", "officer_e2"],
    "Health": ["officer_h1", "officer_h2"],
}


def build_officer_queue_response() -> dict:
    return {
        "message": "Officer queue endpoint ready",
        "officer_id": "mock-officer-id",
        "grievances": [],
        "note": "Database query will be integrated later",
    }


def build_officer_summary_response() -> dict:
    return {
        "message": "Officer analytics summary endpoint ready",
        "summary": {
            "total_assigned": 0,
            "pending": 0,
            "in_progress": 0,
            "resolved": 0,
            "overdue": 0,
        },
        "by_category": [],
        "note": "Real analytics aggregation will be integrated later",
    }


async def assign_least_loaded_officer(category: str, ward: str) -> str:
    """
    Assign the least-loaded officer from the category's officer pool.
    
    Queries MongoDB to find which officer in the category has the fewest
    open grievances (status='routed' or 'pending'). Returns that officer_id.
    If MongoDB is unavailable, returns the first officer in the pool as fallback.
    
    Args:
        category: Complaint category (e.g., "Water Supply", "Roads")
        ward: Ward name (included for context, not used in current logic)
    
    Returns:
        str: Officer ID with the lowest current load
    """
    # Get the list of officers for this category
    officers = DEPT_OFFICERS.get(category, ["officer_general"])
    
    try:
        from app.db.mongo import grievances_collection
        
        # Query MongoDB for each officer to find their current load
        officer_loads = {}
        for officer_id in officers:
            count = await grievances_collection.count_documents({
                "assigned_officer": officer_id,
                "status": {"$in": ["routed", "pending"]}
            })
            officer_loads[officer_id] = count
        
        # Return the officer with the minimum load
        least_loaded = min(officer_loads, key=officer_loads.get)
        logger.info(f"Assigned officer {least_loaded} for category '{category}' (load: {officer_loads[least_loaded]})")
        return least_loaded
    
    except Exception as e:
        logger.warning(
            f"MongoDB query failed for officer assignment: {str(e)}. "
            f"Falling back to first officer in pool."
        )
        # Fallback: return the first officer in the list
        return officers[0]