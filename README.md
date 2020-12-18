# Price Drop Scraper
Allows user to input the URL of a product page from Amazon, Target, or Best Buy, then page will be scraped to pull title and price information.  Products details are stored in a new "tracker.json" file created by the app in the working directory.  The intent is for the app to check the price of each product saved in the "tracker.json" file twice daily and email if the price drops.  However, it's currently designed only for demonstration/testing.  The app does not actually email, or periodically check saved URLs, but you can test both features.  

## Debugging SMTP server
The app is configured to use Python's built-in SMTP server which just prints the email components to the screen rather than actually sending the email.  Copy the code below and paste and execute in a separate shell.  If you do not, the app is still fully functional, but there will be no test emails printed to screen.

python3 -m smtpd -c DebuggingServer -n localhost:1025

## Dependencies
pip install requests
pip install selenium
pip install bs4

The app also assumes that Google Chrome is installed in the default application directory for your operating system.  The Chrome webdriver must be downloaded and stored within the same directory as scraper.py.  The webdriver is required for Selenium and for scraping Amazon and Target's websites because Amazon is good at blocking HTML scrapers and Target is rendered in Javascript.  Go to the link below, download whichever webdriver is compatible with your version of Chrome and OS, unzip the download, then move the 'chromedriver' file to scraper.py's directory.

https://sites.google.com/a/chromium.org/chromedriver/home

The app also uses BeautifulSoup for Best Buy's website.  If there is any issue setting up Selenium, or you don't care for Amazon or Target, the app will still be fully functional for bestbuy.com products. 

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
    - Information about the user's operating system and current working directory is used as well
6. Implement a “scraper” that can be fed a type of file or URL and pull information off of it. For example, a web scraper that lets you provide any website URL and it will
 find certain keywords on the page
    -  App pulls title and price from product page URLs on Amazon, Target, and Best Buy websites.  
