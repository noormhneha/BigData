import sqlite3


def print_to_file(query, params, output_file, question):
    # Connect to the SQLite database
    conn = sqlite3.connect("World.db3")

    cursor = conn.cursor()
    cursor.execute(query, params)  # Execute the query with parameters
    rows = cursor.fetchall()

    # Fetch column names
    cursor.execute(query)
    column_names = [description[0] for description in cursor.description]
    header = " ".join(column_names)

    # Write results to the output file
    with open(output_file, 'a') as f:
        f.write("=" * 55 + f"\nResults for question {question}:\n\n")
        f.write(f"The query:\n{query}\n")
        f.write(f"Num of rows: {len(rows)}\n\n")
        f.write("The results:\n")
        f.write(f"{header}\n")
        for i, row in enumerate(rows[:5]):
            f.write(f"{i} {row}\n")  # Writing each row as a list

        # Print the last 5 rows
        if len(rows) > 5:
            f.write(f"{header}\n")
            for i, row in enumerate(rows[-5:], start=len(rows) - 5):
                f.write(f"{i} {row}\n")  # Writing each row as a list

        f.write("\n")

    # Close the cursor and the connection
    cursor.close()
    conn.close()


output_file = 'query_results.txt'  # output file

# Q1: all the cities
query = """
    SELECT * 
    FROM  City
"""

print_to_file(query, (), output_file, 1)

# Q2: all the countries
query = """
    SELECT * 
    FROM Country
"""
print_to_file(query, (), output_file, 2)

# Q3: display the cities in the country whose code NLD
query = """
    SELECT * 
    FROM City
	WHERE CountryCode = "NLD"
"""

print_to_file(query, (), output_file, 3)

# Q4: Show the countries whose code is LBR or IOT or TKL
query = """
    SELECT * 
    FROM Country
	WHERE Code  IN ('LBR', 'IOT', 'TKL')
"""
print_to_file(query, (), output_file, 4)

# Q5: Show all cities with population above 4 million
query = """
    SELECT * 
    FROM City
    WHERE Population > 4000000
"""
print_to_file(query, (), output_file, 5)

# Q6: Show all cities with population above 3 million in BRA
query = """
    SELECT * 
    FROM City
    WHERE Population > 3000000 AND CountryCode = 'BRA'
"""
print_to_file(query, (), output_file, 6)

# Q6: Show all cities with population between 150k to 170k
query = """
    SELECT * 
    FROM City
    WHERE Population BETWEEN 150000 AND 170000
"""
print_to_file(query, (), output_file, 7)
