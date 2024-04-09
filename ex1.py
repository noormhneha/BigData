import sqlite3

""" install this lib first pls : 
{ pip install tabulate } """

from tabulate import tabulate


def execute_query_and_write_results(query, output_file, question):
    # Connect to the SQLite database
    conn = sqlite3.connect("World.db3")
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)
    rows = cursor.fetchall()

    # Fetch column names
    column_names = [description[0] for description in cursor.description]

    # Extract the first 5 rows
    first_rows = rows[:5]

    # Extract the last 5 rows if available
    if len(rows) > 5:
        last_rows = rows[-5:]
    else:
        last_rows = []

    # Convert rows to a list of lists
    first_data = [[i] + list(row) for i, row in enumerate(first_rows)]
    last_data = [[len(rows) + i - 5] + list(row) for i, row in enumerate(last_rows)]

    # Write results to the output file using tabulate
    with open(output_file, 'a') as f:
        f.write("=" * 55 + f"\nQuestion: {question}\n")
        f.write(f"The query:\n{query}\n")
        f.write(f"Num of rows: {len(rows)}\n")

        f.write("The results:\n")
        if len(rows) > 0:  # first 5 rows
            table = tabulate(first_data, headers=column_names, tablefmt="plain")
            f.write(table + "\n")

            if last_data:  # last 5 rows
                table = tabulate(last_data, headers=column_names, tablefmt="plain")
                f.write(table + "\n")

        f.write("\n")

    # Close the cursor and the connection
    cursor.close()
    conn.close()


def main():
    output_file = 'query_results.txt'  # Output file

    # Define queries and corresponding questions
    queries = [
        # Question 1: All the cities
        ("""
SELECT * 
FROM City
""", 1),

        # Question 2: All the countries
        ("""
SELECT * 
FROM Country
""", 2),

        # Question 3: Display the cities in the country with code NLD
        ("""
SELECT * 
FROM City
WHERE CountryCode = "NLD"
""", 3),

        # Question 4: Show the countries with codes LBR, IOT, or TKL
        ("""
SELECT * 
FROM Country
WHERE Code  IN ('LBR', 'IOT', 'TKL')
""", 4),

        # Question 5: Show all cities with a population above 4 million
        ("""
SELECT * 
FROM City
WHERE Population > 4000000
""", 5),

        # Q6: Show all cities with population above 3 million in BRA
        ("""
SELECT * 
FROM City
WHERE Population > 3000000 AND CountryCode = 'BRA'
""", 6),

        # Q7: Show all cities with population between 150k to 170k
        ("""
SELECT * 
FROM City
WHERE Population BETWEEN 150000 AND 170000
""", 7),

        # Q8: countries indepYear in 1970 or 1980 or 1990
        ("""
SELECT * 
FROM Country
WHERE IndepYear IN (1970, 1980, 1990)
""", 8),

        # Q9: countries indepYear in 1980 and 1990
        ("""
SELECT * 
FROM Country
WHERE IndepYear  = 1980 AND IndepYear = 1990
""", 9),

        # Q10:
        ("""
SELECT *
FROM Country
WHERE IndepYear BETWEEN 1980 AND 1990
""", 10),

        # Q11: In africa and indep at 1964
        ("""
SELECT *
FROM Country
WHERE Continent = 'Africa' AND IndepYear = 1964
""", 11),

        # Q12: countries in africa or indep at 1964
        ("""
SELECT *
FROM Country
WHERE Continent = 'Africa' OR IndepYear = 1964
""", 12),

        # Q13: countries in asia
        ("""
SELECT *
FROM Country
WHERE Continent = 'Asia'
""", 13),

        # Q14: countries not in asia
        ("""
SELECT *
FROM Country
WHERE Continent != 'Asia'
""", 14),

        # Q15: countries not in asia or europe
        ("""
SELECT *
FROM Country
WHERE Continent NOT IN ('Asia', 'Europe')
""", 15),

        # Q16: Cities start with "H"
        ("""
SELECT *
FROM City
WHERE Name LIKE 'H%'
""", 16),

        # Q17: Cities does not includes an 'e'
        ("""
SELECT *
FROM City
WHERE Name NOT LIKE '%e%'
""", 17),

        # Q18: Languages
        ("""
SELECT DISTINCT  Language
FROM CountryLanguage
ORDER BY Language
""", 18),

        # Q19: Countries sorted By indep year and name
        ("""
SELECT *
FROM Country
ORDER BY IndepYear, Name
""", 19),

        # Q20: Sort by LifeExpectancy DESC
        ("""
SELECT *
FROM Country
ORDER BY LifeExpectancy DESC
""", 20),

        # Q21: 10 Highest GNP
        ("""
SELECT *
FROM Country
ORDER BY GNP DESC
LIMIT 10
""", 21),

        # Q22: 10-20 Highest GNP
        ("""
SELECT *
FROM Country
ORDER BY GNP DESC
LIMIT 10,10
""", 22),

        # Q23: Lowest 10 GNP
        ("""
SELECT *
FROM Country
ORDER BY GNP ASC
LIMIT 10
""", 23),

        # Q24: Sort countries by name and in witch region it is
        ("""
SELECT Name, Continent || ' (' || Region || ')'
FROM Country
ORDER BY 1
""", 24),

        # Q25: Countries start with Z - swap the population to m
        ("""
SELECT Name, Population / 1000000.0  Population 
FROM Country
WHERE Name LIKE 'Z%'
""", 25),

        # Q26: Countries Gnp > 2*GNPOld
        ("""
SELECT *
FROM Country
WHERE GNP > 2 * GNPOld
""", 26),

        # Q27: Population / SurfaceArea Order
        ("""
SELECT Name,  Population / SurfaceArea
FROM Country
ORDER BY 2 DESC
""", 27),

        # Q28: Population / SurfaceArea that > 2000, Order by code
        ("""
SELECT Name,  Population / SurfaceArea
FROM Country
WHERE Population / SurfaceArea > 2000
ORDER BY Code DESC
""", 28),

        # Q29: sort by continent and surface area
        ("""
SELECT *
FROM Country
ORDER BY Continent , SurfaceArea DESC
""", 29),

        # Q30: Countries ends with n and less than 10 chars
        ("""
SELECT *``
FROM Country
WHERE Name LIKE '%N' AND LENGTH(Name) <= 10;
""", 30),

        # Q31: All the countries with indep NULL
        ("""
SELECT *
FROM Country
WHERE IndepYear IS NULL
""", 31)
    ]

    # Execute each query and write results to the output file
    for query, question in queries:
        execute_query_and_write_results(query, output_file, question)


if __name__ == "__main__":
    main()
