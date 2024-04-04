import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('World.db3')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()


# Execute the SQL query
query = """
    SELECT * 
    FROM CountryLanguage
    WHERE Language = ? AND IsOfficial = 1
    ORDER BY Percentage DESC
"""
language = 'Arabic'
cursor.execute(query, (language,))

# Fetch all rows from the result
rows = cursor.fetchall()

# Print the results
for row in rows:
    print(row)

# Close the cursor and the connection
cursor.close()
conn.close()
