'''
author: Mark Williams
date: April 19, 2020
description: module used to provide hints & answers for the Web Scraping NB
'''
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'http://www.espn.com/golf/statistics/_/year/2018'

r = requests.get(url)  # HTTP GET request and capturing the response in r
html_doc = r.text  # Extracts the response as html
soup = BeautifulSoup(html_doc)  # creates a BeautifulSoup object to make it easier working with the associated HTML code

# pretty_soup = soup.prettify()
# print(pretty_soup)

# Exercise 1
# HINTS:
#   soup.find_all('td') will return a list of all table cell tags
#   print the `text` attribute (text seen on the web page) for each cell
#   uncomment and run the next line to receive the solution
# %load -r 25:28 scraping_solution.py
table_tags = soup.find_all('td')
for cell in table_tags:
    print(cell.text)

# Exercise 2
# HINTS:
#   <tr> tags include all <td> tags for that table row
#   the find_all method will still return a list
#   each item of the list is also an iterable (each td tag)
#   uncomment and run the next line to receive the solution
# %load -r 36:40 scraping_solution.py
table_tags = soup.find_all('tr')
for cell in table_tags:
    row = [value.text for value in cell]
    print(row)

# Exercise 3
# HINTS:
#   table headings begin with 'RK' as the first two characters
#   use continue to skip subsequent table headings
#   ensure there are 10 values in the list before appending them to table_vals
#   uncomment and run the next line to receive the solution
# %load -r 48:74 scraping_solution.py
# Initialize list containers to store table data
header = []
table_vals = []

# Initialize boolean variable to track whether to store column labels
first = True

table_tags = soup.find_all('tr')
for cell in table_tags:

    if cell.text[:2] == 'RK' and first:
        # header row and first time seeing it
        header = [value.text for value in cell]
        first = False
    elif cell.text[:2] == 'RK':
        # duplicate table heading
        continue
    else:
        # TODO: try to convert each column to its correct type (int or float)
        row = [value.text for value in cell]

        if len(row) == 10:
            table_vals.append(row)

pga = pd.DataFrame(table_vals, columns = header)
pga.info()

# Exercise 4
# HINTS:
#   concatentate the url root with the number to create a new url each iteration
#   can always ignore the table headings now
#   use break in case we are back to Justin Thomas (first page)
#   uncomment and run the next line to receive the solution
# %load -r 82:127 scraping_solution.py
page = True  # used to indicate when to stop iterating over the web pages
page_num = 41  # rank of the first player on the second page
url_root = 'http://www.espn.com/golf/statistics/_/year/2018/count/'

while page:
    try:
        full_url = url_root + str(page_num)
        page_num += 40

        # HTTP GET request and capturing the response in r
        r = requests.get(full_url, timeout = 1)
        html_doc = r.text  # Extracts the response as HTML
        # create a BeautifulSoup object to work with the HTML
        soup = BeautifulSoup(html_doc, features="lxml")

        table_tags = soup.find_all('tr')

        for cell in table_tags:

            if cell.text[:2] == 'RK':
                # table heading
                continue
            else:
                row = [value.text for value in cell]

                if len(row) == 10 and row[0] == '1':
                    page = False
                    break
                elif len(row) == 10:
                    table_vals.append(row)

    except Timeout as excpt:
        print('ERROR: {}'.format(excpt))
        page = False
        
    except HTTPError as excpt:
        print('ERROR: {}'.format(excpt))
        page = False
       
    except ConnectionError as excpt:
        print('ERROR: {}'.format(excpt))
        page = False

pga = pd.DataFrame(table_vals, columns = header)
pga.info()
