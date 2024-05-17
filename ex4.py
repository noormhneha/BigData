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
    output_file = 'query_results_ex4.txt'  # Output file
    # Define queries and corresponding questions
    queries = [

        # 1: Percentage of country area compared to continent for each country
        ("""
SELECT c.Continent, c.Name, 
       ROUND( 100.0 * c.SurfaceArea  / (
			   SELECT SUM(SurfaceArea) 
			   FROM Country ct 
			   WHERE ct.Continent = c.Continent ) , 2) 
       AS PercentOfContinent
FROM Country c
WINDOW w 
AS ( PARTITION BY Continent 
		  ORDER BY PercentOfContinent DESC )
ORDER BY Continent, PercentOfContinent DESC;
""", 1),

        # 2: Cities with population compared to country average
        ("""
SELECT c.Name, c.CountryCode, c.Population,
       CASE WHEN c.Population > (SELECT AVG(Population) FROM City WHERE CountryCode = c.CountryCode) 
            THEN 'Above Average' ELSE 'Below Average' END AS PopulationStatus
FROM City c
ORDER BY c.CountryCode, c.Population;
""", 2),

        # 3: Countries with row number by descending surface area
        ("""
SELECT ROW_NUMBER() OVER (ORDER BY SurfaceArea DESC) AS RowNum, *
FROM Country
ORDER BY RowNum;
""", 3),

        # 4: Countries with row number by ascending indepyear, tied years get same number
        ("""
SELECT DENSE_RANK() OVER (ORDER BY IndepYear) AS RowNum, 
       Name, Code, IndepYear
FROM Country
ORDER BY RowNum, Code;
""", 4),

        # Question 5: Countries ranked by descending number of cities
        ("""
SELECT c.Name, c.Code, 
       RANK() OVER (ORDER BY cnt DESC) AS Rank
FROM Country c
JOIN (SELECT CountryCode, COUNT(*) AS cnt FROM City GROUP BY CountryCode) t
   ON c.Code = t.CountryCode  
ORDER BY Rank DESC;
""", 5),

        # Question 6: Running total population by country with percentage of world
        ("""
SELECT Name, Population, 
       SUM(Population) OVER (ORDER BY Population DESC) AS RunningTotal,
       ROUND(100.0 * SUM(Population) 
						OVER (ORDER BY Population DESC) / (
										SELECT SUM(Population) 
										FROM Country), 2)
						AS PercentOfWorld  
FROM Country;
""", 6),

        # Question 7: Minimum number of countries making up 50% of world population
        ("""
WITH PopulationRanking AS (
  SELECT
    Code AS country_code,
    Population,
    SUM(Population) OVER (ORDER BY Population DESC) AS cumulative_population,
    (SELECT SUM(Population) FROM Country) AS total_population
  FROM Country
)
SELECT
  COUNT(*) AS min_countries_to_reach_half_population
FROM PopulationRanking
WHERE cumulative_population >= (total_population / 2);
""", 7),

        # Question 8: Countries from previous query
        ("""
WITH ctePopRanked AS (
  SELECT Name, Population,
         SUM(Population) OVER (ORDER BY Population DESC) AS RunningTotal  
  FROM Country
)
SELECT Name
FROM ctePopRanked
WHERE RunningTotal <= (SELECT SUM(Population) * 0.5 FROM Country)
ORDER BY RunningTotal DESC;
""", 8),

        # Question 9: Top 2 languages by percentage
        ("""
WITH cte AS (
  SELECT CountryCode, Language, Percentage,
         RANK() OVER (PARTITION BY CountryCode ORDER BY Percentage DESC) AS LanguageRank
  FROM CountryLanguage
)
SELECT CountryCode, 
       MAX(CASE WHEN LanguageRank = 1 THEN Language ELSE NULL END) AS TopLanguage,
       MAX(CASE WHEN LanguageRank = 2 THEN Language ELSE NULL END) AS SecondLanguage
FROM cte
GROUP BY CountryCode;
""", 9),

        # Question 10: Cities ranked by population in country and overall
        ("""
SELECT c.ID, c.Name, c.CountryCode, c.Population,
       RANK() OVER (PARTITION BY c.CountryCode ORDER BY c.Population DESC) AS RankInCountry,
       RANK() OVER (ORDER BY c.Population DESC) AS OverallRank
FROM City c
ORDER BY c.ID;
        
""", 10),

        # Question 11: Number of times life expectancy gap exceeds 1 between consecutive countries
        ("""
SELECT COUNT(*) - 1 AS LifeExpectancyGapsOver1
FROM (
  SELECT LifeExpectancy, 
         LEAD(LifeExpectancy) OVER (ORDER BY LifeExpectancy) AS NextLifeExpectancy
  FROM Country
) t
WHERE ABS(LifeExpectancy - NextLifeExpectancy) > 1;
""", 11),

        # Question 12: Countries with independence 1 and 2 years apart from others
        ("""
SELECT c1.Name
FROM Country c1
JOIN Country c2 ON c2.IndepYear = c1.IndepYear - 1  
JOIN Country c3 ON c3.IndepYear = c1.IndepYear - 2
GROUP BY c1.Name;
""", 12),

        # Question 13: Countries from 7th large independence year gap after 1800
        ("""
WITH SortedCountries AS (
    SELECT name, indepYear, LAG(indepYear) OVER (ORDER BY indepYear, code) AS previous_year
    FROM country
    WHERE indepYear > 1800
),
Gaps AS (
    SELECT name, indepYear, previous_year, indepYear - previous_year AS year_gap
    FROM SortedCountries
    WHERE indepYear - previous_year > 5
),
RankedGaps AS (
    SELECT name, indepYear, year_gap, ROW_NUMBER() OVER (ORDER BY year_gap DESC) AS gap_rank
    FROM Gaps
)
SELECT name, indepYear, year_gap
FROM RankedGaps
WHERE gap_rank >= 7
ORDER BY  indepYear;
""", 13),

        # Question 14a
        ("""
SELECT 
    ci.Name AS City, 
    c.Name AS Country, 
    COUNT(DISTINCT ci.District) AS NumDistricts
FROM City ci
JOIN Country c ON ci.CountryCode = c.Code
-- Join the City table with the Country table using the country code
GROUP BY ci.Name, c.Name
-- Group the results by city name and country name
ORDER BY NumDistricts DESC;
-- Order the results by the number of districts in descending order
""", 14.1),
        # Question 14b
        ("""
SELECT 
    c.Name AS Country, 
    AVG(ci.Population) AS AvgCityPopulation
FROM Country c
JOIN City ci ON c.Code = ci.CountryCode
-- Join the Country table with the City table on the country code
GROUP BY c.Name
-- Group the results by country name
ORDER BY AvgCityPopulation DESC;
-- Order the results by the average city population in descending order
""", 14.2),
        # Question 14c
        ("""
SELECT 
    c.Name AS Country, 
    COUNT(DISTINCT ci.District) AS NumDistricts
FROM Country c
JOIN City ci ON c.Code = ci.CountryCode
-- Join the Country table with the City table on the country code
GROUP BY c.Name
-- Group the results by country name
HAVING COUNT(DISTINCT ci.District) > 3
-- Filter for countries with more than 3 distinct districts
ORDER BY NumDistricts DESC;
-- Order the results by the number of districts in descending order
""", 14.3)
    ]

    # Execute each query and write results to the output file
    for query, question in queries:
        execute_query_and_write_results(query, output_file, question)


if __name__ == "__main__":
    main()