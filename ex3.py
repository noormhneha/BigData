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
    output_file = 'query_results_ex3.txt'  # Output file
    # Define queries and corresponding questions
    queries = [
        # Question 1: Pairs of countries that have the same lang
        ("""
WITH CountryLanguages AS (
  SELECT c.Code AS country_code ,  cl.Language AS language_name
  FROM Country c
  JOIN CountryLanguage cl ON c.Code = cl.CountryCode
)
SELECT cl1.country_code || ' ' || cl2.country_code AS CountryPairs
FROM CountryLanguages cl1
INNER JOIN CountryLanguages cl2 ON cl1.language_name = cl2.language_name
WHERE cl1.country_code != cl2.country_code ;
""", 1),

        # Question 2: Countries with more than 3 lang
        ("""
SELECT Code
FROM Country 
JOIN CountryLanguage ON Code = CountryCode
GROUP BY Code
HAVING COUNT(DISTINCT Language) > 3;
""", 2),

        # Question 3: How many countries with more than 3 lang
        ("""
SELECT COUNT(*)  AS NumOfGroups
FROM (
	SELECT Code
	FROM Country 
	JOIN CountryLanguage ON Code = CountryCode
	GROUP BY Code
	HAVING COUNT(DISTINCT Language) > 3
);
""", 3),

        # Question 4: Only one official language
        ("""
SELECT COUNT(*)  AS OneOfficialLanguages
FROM (
	SELECT Code
	FROM Country 
	JOIN CountryLanguage ON Code = CountryCode
	GROUP BY Code
	HAVING COUNT(Language) = 1 AND SUM(IsOfficial) = 1
);
""", 4),

        # Question 5: The avg LifeExpectancy
        ("""
SELECT COUNT(*)  AS OnlyOfficialLanguages
FROM (
	SELECT Code
	FROM Country 
	JOIN CountryLanguage ON Code = CountryCode
	GROUP BY Code
	HAVING COUNT(Language) = SUM(IsOfficial)
);
""", 5),

        # Question 6: Countries that speaks Hebrew
        ("""
SELECT Name
FROM Country 
JOIN CountryLanguage ON Code = CountryCode
WHERE Language = 'Hebrew';
""", 6),

        # Question 7: Countries that speaks Arabic and English
        ("""
WITH CountryLang AS (
	SELECT c.Code AS CountryCode, cl.Language AS CountryLan
	FROM Country c
	JOIN CountryLanguage cl ON c.Code = cl.CountryCode
)
SELECT Name, Code
FROM Country c
INNER JOIN CountryLang cl ON c.Code = cl.CountryCode
WHERE cl.CountryLan IN ('Arabic', 'English')
GROUP BY c.Code
HAVING COUNT(CountryLan) >= 2;      
""", 7),

        # Question 8: Countries that speaks Arabic or English
        ("""
WITH CountryLang AS (
	SELECT c.Code AS CountryCode, cl.Language AS CountryLan
	FROM Country c
	JOIN CountryLanguage cl ON c.Code = cl.CountryCode
)
SELECT Name, Code
FROM Country c
INNER JOIN CountryLang cl ON c.Code = cl.CountryCode
WHERE cl.CountryLan IN ('Arabic', 'English')      
""", 8),

        # Question 9: Countries that speaks only Arabic and English
        ("""
WITH CountryLang AS (
    SELECT c.Code AS CountryCode, cl.Language AS CountryLan
    FROM Country c
    JOIN CountryLanguage cl ON c.Code = cl.CountryCode
)
SELECT Name
FROM Country c
INNER JOIN CountryLang cl1 ON c.Code = cl1.CountryCode
INNER JOIN CountryLang cl2 ON c.Code = cl2.CountryCode
WHERE cl1.CountryLan = 'Arabic' AND cl2.CountryLan = 'English' AND NOT EXISTS 
(
    SELECT 1
    FROM CountryLang cl_other
    WHERE cl_other.CountryCode = c.Code
    AND cl_other.CountryLan NOT IN ('Arabic', 'English')
);

""", 9),

        # Question 10: Arabic or English but not both
        ("""
SELECT c.Name
FROM Country c
INNER JOIN CountryLanguage cl ON c.Code = cl.CountryCode
WHERE cl.Language IN ('Arabic', 'English')
GROUP BY c.Code
HAVING COUNT(DISTINCT cl.Language) = 1
  AND SUM(CASE WHEN cl.Language NOT IN ('Arabic', 'English') THEN 1 ELSE 0 END) = 0;
""", 10),

        # Question 11: They don't speak English
        ("""
SELECT DISTINCT c.Name
FROM Country c
INNER JOIN CountryLanguage cl ON c.Code = cl.CountryCode
WHERE NOT EXISTS (
    SELECT 1
    FROM CountryLanguage cl2
    WHERE cl2.CountryCode = c.Code
    AND cl2.Language = 'English'
);
""", 11),

        # Question 12: Aabic but not English
        ("""
SELECT DISTINCT c.Name, c.Code
FROM Country c
INNER JOIN CountryLanguage cl ON c.Code = cl.CountryCode
WHERE cl.Language = 'Arabic'
AND NOT EXISTS (
    SELECT 1
    FROM CountryLanguage cl2
    WHERE cl2.CountryCode = c.Code
    AND cl2.Language = 'English'
);
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