from urllib.parse import quote_plus

def search_url(platform: str, query: str) -> str:
    q = quote_plus(query)
    urls = {
        "Amazon": f"https://www.amazon.in/s?k={q}",
        "Flipkart": f"https://www.flipkart.com/search?q={q}",
        "IKEA": f"https://www.ikea.com/in/en/search/?q={q}",
        "Swiggy": f"https://www.swiggy.com/search?query={q}",
        "Zomato": f"https://www.zomato.com/chennai/restaurants/{q}",
        "OYO": f"https://www.oyorooms.com/search?location={q}",
    }
    return urls.get(platform, f"https://www.google.com/search?q={q}")

def fallback_recommendation(planner: str, budget: int, context: dict) -> dict:
    if planner == "home":
        allocations = [("Furniture", .40), ("Lighting", .15), ("Decor", .15), ("Storage", .15), ("Contingency", .15)]
        products = [
            ("Compact study/storage unit", "Storage", .10, "IKEA"),
            ("LED ceiling light", "Lighting", .05, "Amazon"),
            ("Accent wall decor", "Decor", .05, "Flipkart"),
            ("Functional side table", "Furniture", .10, "Amazon"),
        ]
        title = "Budget-friendly home setup"
        summary = f"A practical {context.get('style','modern')} setup across {', '.join(context.get('rooms', []))}."
    elif planner == "party":
        allocations = [("Food & catering", .45), ("Venue", .20), ("Decoration", .15), ("Entertainment", .10), ("Contingency", .10)]
        products = [
            ("Catering package search", "Food & catering", .30, "Swiggy"),
            ("Restaurant/event food search", "Food & catering", .15, "Zomato"),
            ("Hotel/venue options", "Venue", .20, "OYO"),
            ("Party decoration kit", "Decoration", .10, "Amazon"),
        ]
        title = f"{context.get('event_type','Event').title()} budget plan"
        summary = f"A balanced plan for {context.get('guests',0)} guests in {context.get('city','your city')}."
    else:
        allocations = [("Main jewelry", .55), ("Earrings", .20), ("Accessories", .10), ("Contingency", .15)]
        products = [
            ("Occasion necklace set", "Main jewelry", .30, "Amazon"),
            ("Matching earrings", "Earrings", .15, "Flipkart"),
            ("Minimal bracelet", "Accessories", .10, "Amazon"),
        ]
        title = f"{context.get('occasion','Occasion').title()} jewelry plan"
        summary = f"{context.get('style','elegant').title()} options designed to complement the described outfit."
    allocations_out = [{"category": c, "amount": round(budget*p), "percentage": round(p*100,1), "note": "Suggested ceiling for this category."} for c,p in allocations]
    items = []
    for name, cat, frac, platform in products:
        price = max(500, round(budget*frac))
        items.append({"name": name, "category": cat, "estimated_price": price, "platform": platform, "url": search_url(platform, name), "reason": "Fallback suggestion selected to stay within the overall budget."})
    total = sum(x["estimated_price"] for x in items)
    return {"planner": planner, "title": title, "summary": summary, "budget": budget, "estimated_total": total, "remaining_budget": max(0,budget-total), "allocations": allocations_out, "recommendations": items, "tips": ["Compare at least two listings before buying.", "Keep the contingency amount unspent until final costs are known.", "Treat all listed prices as estimates, not live quotes."]}
