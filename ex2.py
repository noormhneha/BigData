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
    if len(rows) >= 10:
        last_rows = rows[-5:]
    else:
        first_rows = rows[:len(rows)]
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
        # Question 1: How many countries in the table
        ("""
SELECT COUNT(*) 
FROM Country
""", 1),

        # Question 2: How many countries in the table with LifeExpectancy
        ("""
SELECT COUNT(*)
FROM Country
WHERE LifeExpectancy 
IS NOT NULL
""", 2),

        # Question 3: How many continent in the table
        ("""
SELECT COUNT(DISTINCT Continent)
FROM Country
""", 3),

        # Question 4: The last IndepYear
        ("""
SELECT MAX(IndepYear)
FROM Country
""", 4),

        # Question 5: The avg LifeExpectancy
        ("""
SELECT AVG(LifeExpectancy)
FROM Country
""", 5),

        # Question 6: The avg LifeExpectancy in countries with surface area above 1m
        ("""
SELECT AVG(LifeExpectancy)
FROM Country
WHERE SurfaceArea > 1000000
""", 6),

        # Question 7a: Name of the country with the largest area
        ("""
SELECT Name
FROM Country
WHERE SurfaceArea = 
	(SELECT MAX(SurfaceArea) 
	FROM Country)        
""", 7.1),
        # Question 7b: Name of the country with the largest area second way [bonus]
        ("""
SELECT Name
FROM Country
ORDER BY SurfaceArea DESC
LIMIT 1         
""", 7.2),

        # Question 8: Name of the country with the smallest area
        ("""
SELECT Name
FROM Country
WHERE SurfaceArea IN 
    (SELECT MIN(SurfaceArea) 
    FROM Country)        
""", 8),

        # Question 9: All the countries in the same region orders by population
        ("""
SELECT Population, Name
FROM Country
WHERE Region IN 
    (SELECT Region 
     FROM Country) 
 ORDER BY Population DESC
""", 9),

        # Question 10: The first 10 countries with population under the avg
        ("""
SELECT Name
FROM Country
WHERE Population < 
    (SELECT AVG(Population) 
    FROM Country) 
ORDER BY Population DESC
LIMIT 10
""", 10),

        # Question 11: The largest GNP and the smallest one. [same row]
        ("""
SELECT MAX(GNP), MIN(GNP)
FROM Country
WHERE GNP > 0
""", 11),

        # Question 12: The largest GNP and the smallest one. [table]
        ("""
SELECT 'max_gdb' AS category, MAX(GNP) AS gdp_value
FROM Country
UNION

SELECT 'min_gdb' AS category, MIN(GNP) AS gdp_value
FROM Country
WHERE GNP > 0
""", 12),

        # Question 13: All the countries that have a population larger 5 times from the avg in the same region
        ("""
SELECT Name
FROM Country AS t1
WHERE Population > 
   (SELECT 5 * AVG(Population)
	FROM Country AS t2
	WHERE t1.Region = t2.Region)
""", 13),

        # Question 14: Num of the citizens in Israel and how much it is from the continent
        ("""
SELECT 
    Population,
    (Population * 100.0 / TotalPopulation) AS Percentage
FROM Country
JOIN 
    (SELECT SUM(Population) AS TotalPopulation 
	FROM Country 
	WHERE Continent = 'Asia')
WHERE Name = 'Israel'
""", 14),

        # Question 15: The cities in countries that indep before BC
        #              ordered by country name, region, city name
        ("""
SELECT city.Name
FROM City
JOIN Country 
ON city.CountryCode = Code 
WHERE IndepYear < 0
ORDER BY Country.Name, Region, city.Name
""", 15),

        # Question 16: All the spoken languages in Europe
        ("""
SELECT DISTINCT Language
FROM CountryLanguage
JOIN Country 
ON CountryLanguage.CountryCode = Code 
WHERE Continent = 'Europe'
""", 16),

        # Question 17: All the spoken lang both in Asia and Europe
        ("""
SELECT DISTINCT Language
FROM CountryLanguage
WHERE CountryCode IN (
    SELECT CountryCode
    FROM CountryLanguage 
    JOIN Country 
	ON CountryLanguage.CountryCode = Code
	AND Continent = 'Europe'
    WHERE Language IN (
        SELECT Language
        FROM CountryLanguage 
        JOIN Country 
		ON CountryLanguage.CountryCode = Code 
		AND Continent = 'Asia')
    )
""", 17),

        # Question 18a: All the spoken lang both Antarctica and Oceania
        ("""
SELECT DISTINCT Language
FROM CountryLanguage 
JOIN Country ON CountryLanguage.CountryCode = Code
WHERE Continent = 'Antarctica'

UNION

SELECT DISTINCT Language
FROM CountryLanguage
JOIN Country ON CountryLanguage.CountryCode =Code
WHERE Continent = 'Oceania'
""", 18.1),
        # Question 18b: All the spoken lang both Antarctica and Oceania [bonus]
        ("""
SELECT DISTINCT Language
FROM CountryLanguage
JOIN Country ON CountryCode = Code
WHERE Continent = 'Antarctica' OR Continent = 'Oceania'
""", 18.2),

        # Question 19a: All the languages that not spoken in Europe
        ("""
SELECT DISTINCT Language
FROM CountryLanguage 
JOIN Country 
ON CountryLanguage.CountryCode = Code
WHERE Continent != 'Europe'
AND Language NOT IN 
	(SELECT DISTINCT Language
    FROM CountryLanguage 
    JOIN Country 
	ON CountryLanguage.CountryCode = Code
    WHERE Continent = 'Europe')
""", 19.1),
        # Question 19b: All the languages that not spoken in Europe [bonus]
        ("""
SELECT DISTINCT Language
FROM CountryLanguage 
JOIN Country 
ON CountryCode = Code
WHERE Continent != 'Europe'

EXCEPT

SELECT DISTINCT Language
FROM CountryLanguage 
JOIN Country 
ON CountryCode = Code
WHERE Continent = 'Europe';
""", 19.2),

        # Question 20: Capitals
        ("""
SELECT Country.Name AS Country, City.Name AS Capital
FROM Country
JOIN City
ON Country.Capital = City.ID
""", 20),

        # Question 21: cities with population > 10% of the country
        ("""
SELECT City.Name AS CityName, City.Population, Country.Name AS CountryName, Country.Population
FROM City
JOIN Country 
ON City.CountryCode = Code
WHERE City.Population > (0.1 * Country.Population);       
""", 21),

        # Question 22: the fourth country by area
        ("""
SELECT Name, SurfaceArea
FROM Country
ORDER BY SurfaceArea DESC
LIMIT 1 OFFSET 3
""", 22),

        # Question 23: LifeExpectancy [Ranges]
        ("""
SELECT Name AS CountryName, LifeExpectancy,
    CASE 
        WHEN LifeExpectancy <= 40 THEN 'LOW'
        WHEN LifeExpectancy <= 70 THEN 'MED'
        WHEN LifeExpectancy <= 100 THEN 'HIGH'
    END AS LifeExpectancyRange
FROM  Country       
""", 23)
    ]

    # Execute each query and write results to the output file
    for query, question in queries:
        execute_query_and_write_results(query, output_file, question)


if __name__ == "__main__":
    main()