from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from pymongo import MongoClient
from statistics import mean

import pymongo

def execute_query_and_write_results(query, output_file, question, db_name):
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[db_name]

    # Execute the query
    results = db.command(query)

    # Write results to the output file
    with open(output_file, 'a') as f:
        f.write("=" * 55 + f"\nQuestion: {question}\n")
        f.write(f"The query:\n{query}\n")
        f.write(f"Num of results: {len(results['result'])}\n")

        f.write("The results:\n")
        for result in results['result'][:5]:
            f.write(str(result) + "\n")

        if len(results['result']) >= 10:
            f.write("Last 5 results:\n")
            for result in results['result'][-5:]:
                f.write(str(result) + "\n")

        f.write("\n")

    # Close the MongoDB connection
    client.close()

def main():
    output_file = 'query_results_ex5.txt'  # Output file
    # Define queries and corresponding questions
    queries = [
        # Question 1a: Houses with more than 50 reviews and either 5+ beds or 2 or fewer beds
        ("""
db.listingsAndReviews.find({
    "property_type": "House",
    "number_of_reviews": {"$gt": 50},
    "$or": [
        {"beds": {"$gte": 5}},
        {"beds": {"$lte": 2}}
    ]
})
        """, 1, "sample_airbnb"),

        # Question 1b: Top 5 neighborhoods with highest average price per person for private rooms
        ("""
db.listingsAndReviews.aggregate([
    {"$match": {"room_type": "Private room"}},
    {"$addFields": {"price_per_person": {"$divide": ["$price", "$accommodates"]}}},
    {"$group": {"_id": "$neighbourhood", "avg_price_per_person": {"$avg": "$price_per_person"}, "count": {"$sum": 1}}},
    {"$sort": {"avg_price_per_person": -1}},
    {"$limit": 5}
])
        """, 2, "sample_airbnb"),

        # Question 1c: Top 5 reviewers by review count
        ("""
db.listingsAndReviews.aggregate([
    {"$unwind": "$reviews"},
    {"$group": {"_id": "$reviews.reviewer_name", "review_count": {"$sum": 1}}},
    {"$sort": {"review_count": 1}},
    {"$limit": 5}
])
        """, 3, "sample_airbnb"),

        # Question 2a: Top 5 movies by comment count
        ("""
db.comments.aggregate([
    {"$group": {"_id": "$movie_id", "comment_count": {"$sum": 1}}},
    {"$sort": {"comment_count": -1}},
    {"$limit": 5},
    {"$lookup": {"from": "movies", "localField": "_id", "foreignField": "_id", "as": "movie_details"}},
    {"$unwind": "$movie_details"},
    {"$project": {"_id": 0, "title": "$movie_details.title", "year": "$movie_details.year", "comment_count": 1}}
])
        """, 4, "sample_mflix"),

        # Question 2b: Directors with 5+ movies and average rating > 7
        ("""
db.movies.aggregate([
    {"$match": {"tomatoes.viewer.rating": {"$gt": 7}}},
    {"$bucket": {
        "groupBy": "$tomatoes.viewer.rating",
        "boundaries": [7, 8, 9, 10],
        "default": "Other",
        "output": {
            "count": {"$sum": 1},
            "directors": {"$addToSet": "$directors"}
        }
    }},
    {"$unwind": "$directors"},
    {"$group": {"_id": "$directors", "movie_count": {"$sum": "$count"}, "avg_rating": {"$avg": "$tomatoes.viewer.rating"}}},
    {"$match": {"movie_count": {"$gte": 5}}},
    {"$project": {"_id": 0, "director": "$_id", "movie_count": 1, "avg_rating": {"$round": ["$avg_rating", 2]}}}
])
        """, 5, "sample_mflix")
    ]

    # Execute each query and write results to the output file
    for query, question, db_name in queries:
        execute_query_and_write_results(query, output_file, question, db_name)

if __name__ == "__main__":
    main()