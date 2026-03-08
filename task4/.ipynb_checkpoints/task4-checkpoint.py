raw_products = [
    ("Laptop", "Electronics", "1200"),
    ("Mouse", "Electronics", 25),
    ("Chair", "Furniture", "85.5"),
    ("Desk", "Furniture", None),
    ("Laptop", "Electronics", "1200"),   # duplicate
    ("Pen", None, "2"),
    ("Monitor", "Electronics", "invalid"),
    ("Table", "Furniture", "150")
]

clean_products = []

for name, category, price in raw_products:
    if category is None:
        continue

    try:
        price = float(price)
    except:
        continue

    clean_products.append((name, category, price))

unique_products = list(set(clean_products))

grouped = {}

for name, category, price in unique_products:

    if category not in grouped:
        grouped[category] = []

    grouped[category].append((name, price))

top_products = {}

for category, items in grouped.items():
    sorted_items = sorted(items, key=lambda x: x[1], reverse=True)
    top_products[category] = sorted_items[:5]

summary = {
    category: {
        "count": len(items),
        "most_expensive": items[0]
    }
    for category, items in top_products.items()
}

print("Top Products Per Category")

for category, items in top_products.items():
    print(f"\n{category}")
    for name, price in items:
        print(name, price)

print("\nSummary")
print(summary)