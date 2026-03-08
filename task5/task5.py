from functools import reduce

orders = [
    (1, "Electronics", 1200),
    (2, "Clothing", 80),
    (3, "Electronics", 300),
    (4, "Groceries", 40),
    (5, "Clothing", 150),
    (6, "Electronics", 50)
]

MIN_ORDER_THRESHOLD = 60

discount_rules = {
    "Electronics" : 0.10,
    "Clothing" : 0.20,
    "Groceries" : 0.05
}

discounted_orders = list(
    map(lambda o: (o[0],o[1],o[2],o[2]*(1 - discount_rules.get(o[1]))), orders)
    )

valid_orders = list(
    filter(
        lambda o: o[3] >= MIN_ORDER_THRESHOLD,
        discounted_orders
    )
)

sorted_orders = sorted(
    valid_orders,
    key=lambda o: o[3],
    reverse=True
)

total_revenue = reduce(
    lambda acc, o: acc + o[3],
    sorted_orders,
    0
)

print("Processed Orders:")
print(sorted_orders)

print("\nTotal Revenue:")
print(total_revenue)