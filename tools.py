from database import get_part, get_by_category

def check_stock(item_name: str) -> dict:
    """Look up quantity and location for a given item."""
    part = get_part(item_name)
    if part:
        return {
            "found": True,
            "name": part["name"],
            "quantity": part["quantity"],
            "location": part["location"]   
        }
    return {"found": False, "message": f"Item '{item_name}' not found in inventory."}


def list_by_category(category: str) -> dict:
    """List all items in a given category."""
    items = get_by_category(category)
    if items:
        return {
            "found": True,
            "category": category,
            "items": items
        }
    return {"found": False, "message": f"No items found in category '{category}'."}

def flag_shortage(item_name: str) -> dict:
    """Log a low-stock flag for an item (no real alerting needed)."""
    print(f"[SHORTAGE FLAG] Low stock reported for: {item_name}")
    return {"flagged": True, "item": item_name}
