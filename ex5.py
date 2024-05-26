from pymongo.mongo_client import MongoClient
import certifi

def execute_query_and_write_results(query, output_file, question, db_name, collection_name):
    # Connect to the MongoDB database
    uri = "mongodb+srv://noormh:Noor1020@atlascluster.7wkowkh.mongodb.net/?retryWrites=true&w=majority&appName=AtlasCluster"
    # Create a new client and connect to the server
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client[db_name]
    collection = db[collection_name]

    # Execute the query
    if isinstance(query, list):
        results = list(collection.aggregate(query))
    else:
        results = list(collection.find(query))

    # Write results to the output file
    with open(output_file, 'a') as f:
        f.write("=" * 55 + f"\nQuestion: {question}\n")
        f.write(f"The query:\n{query}\n")
        f.write(f"Num of results: {len(results)}\n")

        f.write("The results:\n")
        for result in results[:10]:
            f.write(str(result) + "\n")

        f.write("\n")

    # Close the MongoDB connection
    client.close()

def main():
    output_file = 'query_results_ex5.txt'  # Output file
    # Define queries and corresponding questions
    queries = [
        # Question 1a: Houses with more than 50 reviews and either 5+ beds or 2 or fewer beds
        ({
            "property_type": "House",
            "number_of_reviews": {"$gt": 50},
            "$or": [
                {"beds": {"$gte": 5}},
                {"beds": {"$lte": 2}}
            ]
        }, 1.1, "sample_airbnb", "listingsAndReviews"),

        # Question 1b: Top 5 neighborhoods with highest average price per person for private rooms
        ([
            {"$match": {"room_type": "Private room"}},
            {"$addFields": {"price_per_person": {"$divide": ["$price", "$accommodates"]}}},
            {"$group": {"_id": "$neighbourhood", "avg_price_per_person": {"$avg": "$price_per_person"}, "count": {"$sum": 1}}},
            {"$sort": {"avg_price_per_person": -1}},
            {"$limit": 5}
        ], 1.2, "sample_airbnb", "listingsAndReviews"),

        # Question 1c: Top 5 reviewers by review count
        ([
            {"$unwind": "$reviews"},
            {"$group": {"_id": "$reviews.reviewer_name", "review_count": {"$sum": 1}}},
            {"$sort": {"review_count": 1}},
            {"$limit": 5}
        ], 1.3, "sample_airbnb", "listingsAndReviews"),

        # Question 2a: Top 5 movies by comment count
        ([
            {"$group": {"_id": "$movie_id", "comment_count": {"$sum": 1}}},
            {"$sort": {"comment_count": -1}},
            {"$limit": 5},
            {"$lookup": {"from": "movies", "localField": "_id", "foreignField": "_id", "as": "movie_details"}},
            {"$unwind": "$movie_details"},
            {"$project": {"_id": 0, "title": "$movie_details.title", "year": "$movie_details.year", "comment_count": 1}}
        ], 2.1, "sample_mflix", "comments"),

        # Question 2b: Directors with 5+ movies and average rating > 7
        ([
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
        ], 2.2, "sample_mflix", "movies"),

        # Question 3.1: Top 5 restaurants with the highest score in each borough
        ([
            {"$unwind": "$grades"},
            {"$group": {
                "_id": {"borough": "$borough", "name": "$name"},
                "avg_score": {"$avg": "$grades.score"}
            }},
            {"$sort": {"avg_score": -1}},
            {"$group": {
                "_id": "$_id.borough",
                "top_restaurants": {"$push": {"name": "$_id.name", "avg_score": "$avg_score"}}
            }},
            {"$project": {
                "_id": 0,
                "borough": "$_id",
                "top_restaurants": {"$slice": ["$top_restaurants", 5]}
            }}
        ], 3.1, "sample_restaurants", "restaurants"),

        # Question 3.2: Average temperature for each city
        ([
            {"$unwind": "$weather"},
            {"$group": {
                "_id": "$location.city",
                "avg_temp": {"$avg": "$weather.temperature"}
            }},
            {"$sort": {"avg_temp": -1}}
        ], 3.2, "sample_weatherdata", "data")

    ]

    # Execute each query and write results to the output file
    for query, question, db_name, collection_name in queries:
        execute_query_and_write_results(query, output_file, question, db_name, collection_name)

if __name__ == "__main__":
    main()
