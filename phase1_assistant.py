import re
from database import get_all_parts, get_part, get_by_category


def answer_question(question: str) -> str:
    q = question.strip().lower()

    # --- Pattern 1: "how many [item] do we have?" ---
    match = re.search(r"how many (.+?) do we have", q)
    if match:
        item_name = match.group(1).strip()
        part = get_part(item_name)
        if part:
            return f"We have {part['quantity']} {part['name']}."
        return f"I couldn't find '{item_name}' in the inventory."

    # --- Pattern 2: "where is the [item]?" ---
    match = re.search(r"where (?:is|are) (?:the )?(.+?)\??$", q)
    if match:
        item_name = match.group(1).strip()
        part = get_part(item_name)
        if part:
            return f"{part['name']} is stored in the {part['location']}."
        return f"I couldn't find '{item_name}' in the inventory."

    # --- Pattern 3: "list all items in [category]" ---
    match = re.search(r"list all items? in (.+)", q)
    if match:
        category = match.group(1).strip().rstrip(".")
        parts = get_by_category(category)
        if parts:
            names = ", ".join(p["name"] for p in parts)
            return f"Items in {category}: {names}."
        return f"No items found in category '{category}'."

    # --- Fallback: nothing matched ---
    return ("I didn't understand that. Try asking things like "
            "'How many brake pads do we have?', 'Where is the ECU?', "
            "or 'List all items in Electronics.'")


if __name__ == "__main__":
    print(answer_question("How many Brake Pads do we have?"))
    print(answer_question("Where is the ECU?"))
    print(answer_question("List all items in Electronics"))
    print(answer_question("What color is the car?"))
