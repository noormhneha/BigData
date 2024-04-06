import sqlite3

def print_to_file(query, output_file, question):
    # Connect to the SQLite database
    conn = sqlite3.connect("World.db3")

    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    # Fetch column names
    cursor.execute(query)
    column_names = [description[0] for description in cursor.description]
    header = "\t" + "\t".join(column_names)  # Use tabs as separators

    # Write results to the output file
    with open(output_file, 'a') as f:
        f.write("=" * 55 + f"\nResults for question {question}:\n\n")
        f.write(f"The query:\n{query}\n")
        f.write(f"Num of rows: {len(rows)}\n\n")
        if len(rows) > 0:
            f.write("The results:\n")
            f.write(f"{header}\n")
            for i, row in enumerate(rows[:5]):
                f.write(f"{i+1}\t{'\t'.join(str(x) for x in row)}\n")  # Writing each row as a list with tabs as separators

            # Print the last 5 rows
            if len(rows) > 5:
                f.write(f"\n{header}\n")
                for i, row in enumerate(rows[-5:], start=len(rows) - 4):
                    f.write(f"{i}\t{'\t'.join(str(x) for x in row)}\n")  # Writing each row as a list with tabs as separators

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

print_to_file(query, output_file, 1)

# Q2: all the countries
query = """
    SELECT * 
    FROM Country
"""
print_to_file(query, output_file, 2)

# Q3: display the cities in the country whose code NLD
query = """
    SELECT * 
    FROM City
	WHERE CountryCode = "NLD"
"""

print_to_file(query, output_file, 3)

# Q4: Show the countries whose code is LBR or IOT or TKL
query = """
    SELECT * 
    FROM Country
	WHERE Code  IN ('LBR', 'IOT', 'TKL')
"""
print_to_file(query, output_file, 4)

# Q5: Show all cities with population above 4 million
query = """
    SELECT * 
    FROM City
    WHERE Population > 4000000
"""
print_to_file(query, output_file, 5)

# Q6: Show all cities with population above 3 million in BRA
query = """
    SELECT * 
    FROM City
    WHERE Population > 3000000 AND CountryCode = 'BRA'
"""
print_to_file(query, output_file, 6)

# Q7: Show all cities with population between 150k to 170k
query = """
    SELECT * 
    FROM City
    WHERE Population BETWEEN 150000 AND 170000
"""
print_to_file(query, output_file, 7)

# Q8: countries indepYear in 1970 or 1980 or 1990
query = """
    SELECT * 
    FROM Country
    WHERE IndepYear IN (1970, 1980, 1990)
"""
print_to_file(query, output_file, 8)

# Q9: countries indepYear in 1980 and 1990
query = """
	SELECT * 
	FROM Country
	WHERE IndepYear  = 1980 AND IndepYear = 1990
"""
print_to_file(query, output_file, 9)

# Q10:
query = """
    SELECT *
    FROM Country
    WHERE IndepYear BETWEEN 1980 AND 1990
"""
print_to_file(query, output_file, 10)

# Q11: In africa and indep at 1964
query = """
    SELECT *
    FROM Country
    WHERE Continent = 'Africa' AND IndepYear = 1964
"""
print_to_file(query, output_file, 11)

# Q12: countries in africa or indep at 1964
query = """
    SELECT *
    FROM Country
    WHERE Continent = 'Africa' OR IndepYear = 1964
"""
print_to_file(query, output_file, 12)

# Q13: countries in asia
query = """
    SELECT *
    FROM Country
    WHERE Continent = 'Asia'
"""
print_to_file(query, output_file, 13)

# Q14: countries not in asia
query = """
    SELECT *
    FROM Country
    WHERE Continent != 'Asia'
"""
print_to_file(query, output_file, 14)

# Q15: countries not in asia or europe
query = """
    SELECT *
    FROM Country
    WHERE Continent NOT IN ('Asia', 'Europe')
"""
print_to_file(query, output_file, 15)

# Q16: Cities start with "H"
query = """
    SELECT *
    FROM City
    WHERE Name LIKE 'H%'
"""
print_to_file(query, output_file, 16)

# Q17: Cities does not includes an 'e'
query = """
    SELECT *
    FROM City
    WHERE Name NOT LIKE '%e%'
"""
print_to_file(query, output_file, 17)

# Q18: Languages
query = """
    SELECT DISTINCT  Language
    FROM CountryLanguage
	ORDER BY Language
"""
print_to_file(query, output_file, 18)

# Q19: Countries sorted By indep year and name
query = """
    SELECT *
    FROM Country
	ORDER BY IndepYear, Name
"""
print_to_file(query, output_file, 19)

# Q20: Sort by LifeExpectancy DESC
query = """
    SELECT *
    FROM Country
	ORDER BY LifeExpectancy DESC
"""
print_to_file(query, output_file, 20)

# Q21: 10 Highest GNP
query = """
    SELECT *
    FROM Country
	ORDER BY GNP DESC
	LIMIT 10
"""
print_to_file(query, output_file, 21)

# Q22: 10-20 Highest GNP
query = """
    SELECT *
    FROM Country
	ORDER BY GNP DESC
	LIMIT 10,10
"""
print_to_file(query, output_file, 22)

# Q23: Lowest 10 GNP
query = """
    SELECT *
    FROM Country
	ORDER BY GNP ASC
	LIMIT 10
"""
print_to_file(query, output_file, 23)

# Q24: Sort countries by name and in witch region it is
query = """
    SELECT Name, Continent || ' (' || Region || ')'
    FROM Country
	ORDER BY 1
"""
print_to_file(query, output_file, 24)

# Q25: Countries start with Z - swap the population to m
query = """
    SELECT Name, Population / 1000000.0  Population 
    FROM Country
    WHERE Name LIKE 'Z%'
"""
print_to_file(query, output_file, 25)

# Q26: Countries Gnp > 2*GNPOld
query = """
    SELECT *
    FROM Country
    WHERE GNP > 2 * GNPOld
"""
print_to_file(query, output_file, 26)

# Q27: Population / SurfaceArea Order
query = """
    SELECT Name,  Population / SurfaceArea
    FROM Country
    ORDER BY 2 DESC
"""
print_to_file(query, output_file, 27)

# Q28: Population / SurfaceArea that > 2000, Order by code
query = """
    SELECT Name,  Population / SurfaceArea
    FROM Country
    WHERE Population / SurfaceArea > 2000
    ORDER BY Code DESC
"""
print_to_file(query, output_file, 28)

# Q29: sort by continent and surface area
query = """
    SELECT *
    FROM Country
    ORDER BY Continent , SurfaceArea DESC
"""
print_to_file(query, output_file, 29)

# Q30: Countries ends with n and less than 10 chars
query = """
    SELECT *
    FROM Country
    WHERE Name LIKE '%N' AND LENGTH(Name) <= 10;
"""
print_to_file(query, output_file, 30)

# Q31: All the countries with indep NULL
query = """
    SELECT *
    FROM Country
    WHERE IndepYear IS NULL
"""
print_to_file(query, output_file, 31)