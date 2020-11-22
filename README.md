# Price Drop Scraper
Allows user to input the URL of a product page from Amazon or Target.  App will scrape the page for the current price, and then continue to scrape twice a day after.  User will receive an email if the price drops lower than the original price.

## Debugging SMTP server
For testing purposes, the app does actually email.  It's setup to use Python's built-in SMTP server which just prints the message to the screen.  Copy the code below and paste and execute in a terminal shell. 

### Mac & Linux terminal
sudo python3 -m smtpd -c DebuggingServer -n localhost:1025

### Windows command prompt
python -m smtpd -c DebuggingServer -n localhost:1025

## Requirements
pip install requests-html
pip install pyppdf
