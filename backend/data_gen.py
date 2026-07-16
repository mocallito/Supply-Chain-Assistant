import random
import pandas as pd
from datetime import datetime, timedelta

NUM_ROWS = 1000_000
OUTPUT_FILE = "reviews_1mil.csv"

random.seed(42)

titles = [
    "Best pizza in town",
    "Amazing burger experience",
    "Fantastic pasta",
    "Loved the sushi",
    "Excellent coffee",
    "Great breakfast spot",
    "Highly recommend this place",
    "Wonderful dining experience",
    "Best tacos ever",
    "Delicious ramen",
]

foods = [
    "pepperoni pizza",
    "margherita pizza",
    "cheeseburger",
    "ramen",
    "sushi rolls",
    "pasta",
    "tacos",
    "fried chicken",
    "steak",
    "salmon",
]

positive_adj = [
    "crispy", "juicy", "fresh", "flavorful",
    "perfectly cooked", "tender", "delicious"
]

negative_adj = [
    "bland", "cold", "dry", "overcooked",
    "burnt", "greasy"
]

positive_endings = [
    "Will definitely be back!",
    "Highly recommended.",
    "Great value for money.",
    "Can't wait to visit again.",
]

negative_endings = [
    "Probably won't return.",
    "Expected much better.",
    "Not worth the price.",
]

service_comments = [
    "The staff were friendly and attentive.",
    "Service was quick and professional.",
    "The atmosphere was cozy and welcoming.",
    "Everything arrived fresh and hot.",
]


def random_date():
    start = datetime(2020, 1, 1)
    end = datetime(2025, 12, 31)
    return (
        start + timedelta(days=random.randint(0, (end - start).days))
    ).strftime("%Y-%m-%d")


def generate_review(rating):
    food = random.choice(foods)

    if rating >= 4:
        return (
            f"The {food} was {random.choice(positive_adj)}. "
            f"{random.choice(service_comments)} "
            f"{random.choice(positive_endings)}"
        )
    elif rating == 3:
        return (
            f"The {food} was decent. "
            f"{random.choice(service_comments)} "
            "Overall it was an average experience."
        )
    else:
        return (
            f"The {food} was {random.choice(negative_adj)}. "
            f"{random.choice(service_comments)} "
            f"{random.choice(negative_endings)}"
        )


# Weighted ratings (mostly positive)
ratings = random.choices(
    [1, 2, 3, 4, 5],
    weights=[5, 8, 15, 30, 42],
    k=NUM_ROWS,
)

df = pd.DataFrame({
    "Title": random.choices(titles, k=NUM_ROWS),
    "Date": [random_date() for _ in range(NUM_ROWS)],
    "Rating": ratings,
    "Review": [generate_review(r) for r in ratings],
})

df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved {len(df):,} rows to {OUTPUT_FILE}")
