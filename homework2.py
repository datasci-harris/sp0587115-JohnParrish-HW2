"""
Write your answers in the space between the questions, and commit/push only
this file (homework2.py) and countries.csv to your repo. Note that there can 
be a difference between giving a "minimally" right answer, 
and a really good answer, so it can pay to put thought into your work. 

This is a much longer project than those you've done in class - remember to use
comments to help readers navigate your work!

To answer these questions, you will use the two csv files provided in the repo.
The file named gdp.csv contains the per capita GDP of many countries in and 
around Europe in 2023 US dollars. The file named population.csv contains 
estimates of the population of many countries.
"""
import pandas as pd


"""
QUESTION 1

Short: Open the data

Long: Load the GDP data into a dataframe. Specify an absolute path using the Python 
os library to join filenames, so that anyone who clones your homework repo 
only needs to update one string for all loading to work.
"""
##imports required package
import os

##base path for working on project
base_path = r"C:\Users\Jay\OneDrive\Desktop\Snake 1\Homework 2"

##preset variables for existing csv files
gdp_path = os.path.join(base_path, "gdp.csv")
pop_path = os.path.join(base_path, "population.csv")

##loads csv files into working variables
gdp = pd.read_csv(gdp_path)
population = pd.read_csv(pop_path)


"""
QUESTION 2

Short: Clean the data

Long: There are numerous issues with the data, on account of it having been 
haphazardly assembled from an online table. To start with, the column containing
country names has been labeled TIME. Fix this.

Next, trim this down to only member states of the European Union. To do this, 
find a list of members states (hint: there are 27 as of Apr 2024) and manually 
create your own CSV file with this list. Name this file countries.csv. Load it 
into a dataframe. Merge the two dataframes and keep only those rows with a 
match.

(Hint: This process should also flag the two errors in naming in gdp.csv. One 
 country has a dated name. Another is simply misspelt. Correct these.)
"""
##renames "time" column with country name
gdp.rename(columns = {"TIME": "country"}, inplace = True)

##fixes data errors by renaming Italy and Czech Republic appropriately and for consistency
gdp["country"] = gdp["country"].replace("Itly", "Italy")
gdp["country"] = gdp["country"].replace("Czechia", "Czech Republic")

##created new countries csv existing of EU member states, reads csv back in as variable
countries_path = os.path.join(base_path, "countries.csv")
countries = pd.read_csv(countries_path)

##merges countries csv and gdp csv to create df of only EU member states
gdp_merge = gdp.merge(countries, 
                      on = "country",
                      how = "inner")
"""
QUESTION 3

Short: Reshape the data

Long: Convert this wide data into long data with columns named year and gdp.
The year column should contain int datatype objects.

Remember to convert GDP from string to float. (Hint: the data uses ":" instead
of NaN to denote missing values. You will have to fix this first.) 
"""
##reshapes the data from wide to long
gdp_merge = gdp_merge.melt(id_vars = "country",
                      var_name = "year",
                      value_name = "gdp")

##replaces ":" valye in gdp with NaN; removes "GDP" from year data
gdp_merge["gdp"] = gdp_merge["gdp"].str.replace(":", "NaN")
gdp_merge["year"] = gdp_merge["year"].str.replace("GDP", "")

##converts year and gdp values to integers and floats respectively
gdp_merge["year"] = gdp_merge["year"].astype(int)
gdp_merge["gdp"] = gdp_merge["gdp"].astype(float)

"""
QUESTION 4"

Short: Repeat this process for the population data.

Long: Load population.csv into a dataframe. Rename the TIME columns. 
Merge it with the dataframe loaded from countries.csv. Make it long, naming
the resulting columns year and population. Convert population and year into int.
"""
##renames "time" column with country name
population.rename(columns = {"TIME": "country"}, inplace = True)

##merges countries csv and gdp csv to create df of only EU member states
pop_merge = population.merge(countries, 
                on = "country",
                how = "inner")

##reshapes the data from wide to long
pop_merge = pop_merge.melt(id_vars = "country",
                           var_name = "year",
                           value_name = "population")

##converts year and gdp values to integers and floats respectively
pop_merge["year"] = pop_merge["year"].astype(int)
pop_merge["population"] = pop_merge["population"].astype(int)

"""
QUESTION 5

Short: Merge the two dataframe, find the total GDP

Long: Merge the two dataframes. Total GDP is per capita GDP times the 
population.
"""
##merges both pop and gdp df together on country and year
final_merge = pd.merge( gdp_merge, pop_merge,
                        on = ["country", "year"],
                        how = "outer")

##creates function to calculate total gdp
def total_gdp(row):
    ##if values are not NA creates the total gdp value, if the value is NA function will return NA
    if pd.notna(row["gdp"]) and pd.notna(row["population"]):
        gdp_product = row["population"] * row["gdp"]
        return gdp_product
    else:
        return "NaN"

##applies the above function to the final merge dataframe and creates a total gdp column
final_merge["Total GDP"] = final_merge.apply(total_gdp, axis = 1)

##ensures total gdp value is a float
final_merge["Total GDP"] = final_merge["Total GDP"].astype(float)
"""
QUESTION 6

Short: For each country, find the annual GDP growth rate in percentage points.
Round down to 2 digits.

Long: Sort the data by name, and then year. You can now use a variety of methods
to get the gdp growth rate, and we'll suggest one here: 

1. Use groupby and shift(1) to create a column containing total GDP from the
previous year. We haven't covered shift in class, so you'll need to look
this method up. Using groupby has the benefit of automatically generating a
missing value for 2012; if you don't do this, you'll need to ensure that you
replace all 2012 values with missing values.

2. Use the following arithematic operation to get the growth rate:
    gdp_growth = (total_gdp - total_gdp_previous_year) * 100 / total_gdp
"""
##imports math library to do rounding
import math

##sorts dataframe by country and year
sorted_list = final_merge.sort_values(by = ["country", "year"], ascending = [True, True])

##creates groupby object to create previous year gdp column
sorted_list["previous_year_gdp"] = sorted_list.groupby("country")["Total GDP"].shift(1)

##creates gdp growth column
sorted_list["gdp_growth"] = (sorted_list["Total GDP"] - sorted_list["previous_year_gdp"]) * 100 / sorted_list["Total GDP"]

##function to round gdp growth values down to two digits
def rounding(value):
    if pd.notna(value): 
        return math.floor(value * 100) / 100
    else:
        return "NaN"

##applies rounding function to gdp growth value
sorted_list["gdp_growth"] = sorted_list["gdp_growth"].apply(rounding)

##ensures gdp growth value is a float
sorted_list["gdp_growth"] = sorted_list["gdp_growth"].astype(float)

"""
QUESTION 7

Short: Which country has the highest total gdp (for the any year) in the EU? 

Long: Do not hardcode your answer! You will have to put the automate putting 
the name of the country into a string called country_name and using the following
format string to display it:

print(f"The largest country in the EU is {country_name}")
"""
##new groupbyobject identifying total gdp for each country
gdp_totals = sorted_list.groupby("country")["Total GDP"]

##creates new varibale with highest gdp value for each country
max_gdp_by_country = gdp_totals.max()

##creates variable with the name of the country that has the highest gdp of the max gdp values
country_name = max_gdp_by_country.idxmax()

##prints out the name of the country with the highest gdp value
print(f"The largest country in the EU is {country_name}")

"""
QUESTION 8

Create a dataframe that consists only of the country you found in Question 7

In which year did this country have the most growth in the period 2012-23?

In which year did this country have the least growth in the peroid 2012-23?

Do not hardcode your answer. You will have to use the following format strings 
to show your answer:

print(f"Their best year was {best_year}")
print(f"Their worst year was {worst_year}")
"""
##creates new data frame that only has values for Germany
germany_data = sorted_list[sorted_list["country"] == "Germany"]


##identifies the years of maximum and minimum gdp growth
best_year = germany_data.loc[germany_data["gdp_growth"].dropna().idxmax(), "year"]
worst_year = germany_data.loc[germany_data["gdp_growth"].dropna().idxmin(), "year"]

##prints the maximum and minimum gdp growth rates for Germany
print(f"Their best year was {best_year}")
print(f"Their worst year was {worst_year}")