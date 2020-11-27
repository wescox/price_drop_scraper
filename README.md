# Price Drop Scraper
Allows user to input the URL of a product page from Amazon or Target.  App will scrape the page for the current price, and then continue to scrape twice a day after.  User will receive an email if the price drops lower than the original price.

## Debugging SMTP server
For testing purposes, the app does not actually email.  It's setup to use Python's built-in SMTP server which just prints the message to the screen.  Copy the code below and paste and execute in a terminal shell.  If you do not, the app still works and scrapes, but there will be an error and no test emails will be sent.

### Mac & Linux terminal
sudo python3 -m smtpd -c DebuggingServer -n localhost:1025

### Windows command prompt
python -m smtpd -c DebuggingServer -n localhost:1025

## Dependencies
pip install requests-html\
pip install pyppdf\
pip install bs4

## Required Features List
1. Implement a “master loop” console application where the user can repeatedly enter commands/perform actions, including choosing to exit the program
    - The user interface meets this requirement
2. Create a dictionary or list, populate it with several values, retrieve at least one value, and use it in your program
    - Lists and dictionaries are used often.  The trackers.json file is a dictionary with lists of other dictionaries as values.  
3. Read data from an external file, such as text, JSON, CSV, etc and use that data in your application
    - Data is read from 2 different json files, one of which is created by the app. 
4. Create and call at least 3 functions, at least one of which must return a value that is used
    - There are many functions, all of which return a value used elsewhere.  
5. Calculate and display data based on an external factor (ex: get the current date, and display how many days remaining until some event)
    - App compares current external price to previously stored prices at certain times of day
6. Implement a “scraper” that can be fed a type of file or URL and pull information off of it. For example, a web scraper that lets you provide any website URL and it will
 find certain keywords on the page
    -  App pulls title and price from product page URLs on Amazon, Target, and Best Buy websites.  
