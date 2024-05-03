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

        # Question 13: Spoken languages in 2 countries or more
        ("""
SELECT Language
FROM CountryLanguage
GROUP BY Language
HAVING COUNT(DISTINCT CountryCode) >= 2
""", 13),

        # Question 14:  Spoken languages in exactly 2 countries
        ("""
SELECT Language
FROM CountryLanguage
GROUP BY Language
HAVING COUNT(DISTINCT CountryCode) = 2
""", 14),

        # Question 15: Alphabite counter lang
        ("""
SELECT SUBSTRING(Name, 1, 1) AS Letter, COUNT(*) AS Counter
FROM City
GROUP BY Letter
ORDER BY Letter
""", 15),

        # Question 16: countries that all the lang start in the same letter
        ("""
SELECT CountryName
FROM (
    SELECT c.Name AS CountryName, SUBSTRING(cl.Language, 1, 1) AS FirstLetter
    FROM Country c
    JOIN CountryLanguage cl ON c.Code = cl.CountryCode
) AS CountryLanguages
GROUP BY CountryName
HAVING COUNT(DISTINCT FirstLetter) = 1 AND COUNT(*) > 1;
""", 16),

        # Question 17: Country + lang
        ("""
WITH RankedLanguages AS (
    SELECT 
        c.Name AS CountryName, 
        cl.Language,
        ROW_NUMBER() OVER (PARTITION BY c.Name ORDER BY cl.Language) AS LanguageRank
    FROM Country c
    JOIN CountryLanguage cl ON c.Code = cl.CountryCode
)
SELECT CountryName, Language
FROM RankedLanguages
WHERE LanguageRank = 1;

""", 17),

        # Question 18: All the official lang
        ("""
SELECT  c.Name AS CountryName,  cl.Language AS OfficialLanguage
FROM Country c
JOIN CountryLanguage cl ON c.Code = cl.CountryCode
WHERE cl.IsOfficial = '1'
ORDER BY CountryName, OfficialLanguage;
""", 18),

        # Question 19: countries with the most diff lang
        ("""
WITH CountryLang AS (
    SELECT c.Code AS CountryCode, cl.Language AS CountryLan
    FROM Country c
    JOIN CountryLanguage cl ON c.Code = cl.CountryCode
)
SELECT c.Name,  COUNT(*) AS LanguageCount
FROM Country c
INNER JOIN CountryLang cl ON c.Code = cl.CountryCode
GROUP BY c.Name
ORDER BY LanguageCount DESC
LIMIT 3;

""", 19),

        # Question 20: percentage of its surface area relative to its continent
        ("""
WITH ContinentSurfaceArea AS (
	SELECT Continent, SUM(SurfaceArea) AS TotalSurfaceArea
	FROM  Country
	GROUP BY  Continent
)
SELECT  c.Name AS CountryName, (c.SurfaceArea / cs.TotalSurfaceArea) * 100 AS SurfaceAreaPercentage
FROM Country c
JOIN ContinentSurfaceArea cs ON c.Continent = cs.Continent;
""", 20),

        # Question 21: The avg of lang in each country
        ("""
WITH LanguageCount AS (
    SELECT CountryCode, COUNT(Language) AS NumLanguages
    FROM CountryLanguage
    GROUP BY CountryCode
)
SELECT c.Name AS CountryName, AVG(lc.NumLanguages) AS AvgNumLanguages
FROM Country c
LEFT JOIN LanguageCount lc ON c.Code = lc.CountryCode
GROUP BY c.Name;   
""", 21),

        # Question 22
        ("""
SELECT
    -- 1. Count of countries that got independent after 1950
    (
	SELECT COUNT(*) 
	FROM Country 
	WHERE IndepYear > 1950
	) AS After1950,
    
    -- 2. Average life expectancy in Africa
    (
	SELECT AVG(LifeExpectancy) 
	FROM Country 
	WHERE Continent = 'Africa') 
	AS AvgLifeExpectancyInAfrica,
    
    -- 3. Difference between the max and min population of countries in Europe
    (SELECT MAX(Population) - MIN(Population) 
	FROM Country 
	WHERE Continent = 'Europe') 
	AS PopulationDifferenceInEurope;
""", 22),

        # Question 23: city detaials
        ("""
SELECT ci.Name AS CityName, co.Name AS CountryName,
		(SELECT GROUP_CONCAT(cl.Language, ' - ')
		 FROM CountryLanguage cl
		 WHERE ci.CountryCode = cl.CountryCode
		 GROUP BY cl.CountryCode) AS Languages
FROM City ci
INNER JOIN Country co ON ci.CountryCode = co.Code
WHERE ci.Population > 500000;

""", 23),

        # Question 24: country lang pairs
        ("""
WITH CountryLanguages AS (
  SELECT c.Code AS country_code ,  cl.Language AS language_name
  FROM Country c
  JOIN CountryLanguage cl ON c.Code = cl.CountryCode
)
SELECT DISTINCT 
		CASE WHEN cl1.country_code < cl2.country_code 
					THEN cl1.country_code || ' ' || cl2.country_code
		 ELSE cl2.country_code || ' ' || cl1.country_code 
		 END AS CountryPairs
FROM CountryLanguages cl1
INNER JOIN CountryLanguages cl2 
		ON cl1.country_code != cl2.country_code
		AND cl1.language_name = cl2.language_name
GROUP BY CountryPairs
HAVING COUNT(DISTINCT cl1.language_name) >= 2;
""", 24),

        ("""
SELECT c.Name AS Country,
				  c.GNP AS GNP_orig,
				  v.v,
				  v.v * c.GNP AS GNP_new
FROM Country c
CROSS JOIN
		(SELECT 3 AS v UNION ALL
		 SELECT 11 UNION ALL
		 SELECT 20) 
		 AS v
ORDER BY Country
""", 25),

        ("""
WITH LanguagePercentage AS (
    SELECT 
        cl.CountryCode,
        cl.Language,
        cl.Percentage,
        SUM(cl.Percentage) OVER (PARTITION BY cl.CountryCode ORDER BY cl.Percentage) AS percent_agg_sum
    FROM 
        CountryLanguage cl
)
SELECT 
    CountryCode,
    Language,
    Percentage,
    percent_agg_sum
FROM 
    LanguagePercentage
ORDER BY 
    CountryCode, Percentage;
        
""", 26),

        ("""
WITH RankedLanguages AS (
    SELECT 
        cl.CountryCode,
        cl.Language,
        cl.Percentage,
        ROW_NUMBER() OVER (PARTITION BY cl.CountryCode ORDER BY cl.Percentage DESC) AS LanguageRank
    FROM 
        CountryLanguage cl
)
SELECT  CountryCode, Language, Percentage
FROM  RankedLanguages
WHERE  LanguageRank = 1;        
""", 27)
    ]

    # Execute each query and write results to the output file
    for query, question in queries:
        execute_query_and_write_results(query, output_file, question)


if __name__ == "__main__":
    main()