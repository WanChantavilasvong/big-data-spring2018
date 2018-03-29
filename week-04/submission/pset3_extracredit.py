import requests
import bs4

#Get webpage
response = requests.get('https://en.wikipedia.org/wiki/List_of_countries_by_greenhouse_gas_emissions')
soup = bs4.BeautifulSoup(response.text, "html.parser")

#Open a new csv file
f = open('week-04/submission/gas_emission_countries.csv','a')

#Extract table: modfied code from RocketDonkey founded in https://stackoverflow.com/questions/14167352/beautifulsoup-html-csv
data = soup.find('table', attrs={ "class" : "wikitable sortable"})

#Write header manually because the existing header has \n, which will become problematic with csv.
f.write("Country, GHG_Emission, Perc_Global\n")

row = data.find_all('tr')
del row[0:2] #Delete the header row (is already written) and the World row (is not wanted)

for i in range(len(row)):
    #Find cells in row
    cell = row[i].find_all('td')
    #Write the 1st cell, specifically for a_tag
    #There's still problems with encoding some unicodes, but I am able to get the majority of the data
    f.write(cell[0].a.string + ", ")
    #Write the 2nd cell
    f.write(cell[1].string + ", ")
    #Write the last cell ending in a new line
    f.write(cell[2].string + "\n")

f.close() # close file
