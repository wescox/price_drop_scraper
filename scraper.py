# #html = soup.prettify("utf-8")
# # with open("output2.html", "wb") as file:
# #     file.write(html)

# TODO: add regex for retailer in scrape
# TODO: make help interactive

# libraries
import smtplib
import json
#import time
import requests
from random import choice
from sys import exit
from os import system
from requests_html import HTMLSession
from pyppdf import patch_pyppeteer #only needed for Mac
from bs4 import BeautifulSoup


# notification email
def send_mail():
    sender = 'from@fromdomain.com'
    receivers = ['to@todomain.com']
    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    This is a test e-mail message.
    """
    try:
        smtpObj = smtplib.SMTP('localhost', 1025)
        smtpObj.sendmail(sender, receivers, message)         
        print("Successfully sent email")
    except:
        print("Error: unable to send email")


# open spoof browser session
def get_session(url):
    if "target.com" in url:
        s = HTMLSession()
        page = s.get(url)
        page.html.render(sleep=1)
    else:
        with open('headers.json') as file:
            data = json.load(file)
        header = data[choice(list(data.keys()))]
        r = requests.Session()
        response = r.get(url, headers = header)
        page = BeautifulSoup(response.content, 'lxml')
    return page


# update json file
def update_json(trackers, file = 'tracker.json'):
    with open(file, 'w') as f:
        json.dump(trackers, f, indent = 4)

        
# web scraper
def scrape(url):
    print("\nProcessing...\n")
    page = get_session(url)
    dict = {'title': '', 'price': '', 'url': url}
    if "target.com" in url:
        price = page.html.xpath('/html/body/div[1]/div/div[5]/div/div[2]/div[2]/div[1]/div[1]/div[1]', first = True).text.strip()
        dict['title'] = page.html.xpath('/html/body/div[1]/div/div[5]/div/div[1]/div[2]/h1/span', first = True).text.strip()
        retailer = 'target.com'
    elif "amazon.com" in url:
        try:
            price = page.find(id="priceblock_ourprice").get_text() # regular price
        except:
             price = page.find(id="priceblock_dealprice").get_text() # sale price
        dict['title'] = page.find(id="productTitle").get_text().strip()
        retailer = 'amazon.com'
    elif "bestbuy.com" in url:
        price = page.find(attrs = {'class':'priceView-hero-price priceView-customer-price'}).span.get_text()
        dict['title'] = page.find(attrs = {'class':'sku-title'}).get_text()
        retailer = 'bestbuy.com'
    dict['price'] = float(price[1:])
    trackers[retailer].append(dict)
    update_json(trackers)
    print("{} tracker successfully added\n".format(retailer))


# check if user input is an app command
def menu_option(ui, active = False):
    if ui.lower() == 'q':
        exit()
    elif ui.lower() == 'h':
        #menu_help()
        pass
    elif ui.lower() == 'p':
        menu_addproduct()
    elif ui.lower() in ('v', 'r'):
        menu_removeproduct()
    else:
        if active:
            return
        else:
            print("\nInvalid command.")
            ui = input("\nWhat would you like to do:\n")
            menu_option(ui)


# welcome interface
def welcome():
    system('clear')
    print("Price Drop Scraper will monitor the price of chosen products from popular retailers and email you if the price drops.\n\nYou can track products from these online retailers: Amazon, Target, Best Buy\n")
    print(commands)
    ui = input("What would you like to do:\n")
    menu_option(ui)


# interface for adding products to json
def menu_addproduct():
    system('clear')
    while True:
        print(commands)
        ui = input("Copy/paste the complete URL from a product page you want to track or enter a command:\n")
        menu_option(ui, True)
        try:
            scrape(ui)
        except:
            print("\nERROR: Incompatible URL or invalid command.\nRemember you can only track from Amazon, Target, and Best Buy.\nAmazon doesn't like scrapers and may have blocked your attempt.\nTry again.\n")


# interface for removing products from json
def menu_removeproduct():
    system('clear')
    while True:
        count = 0
        tmp_list = []
        for retailer in trackers:
            tracker_count = 0
            print(retailer + ':')
            for key in trackers[retailer]:
                count += 1
                tmp_list.append([retailer, key['title'], tracker_count])
                tracker_count += 1
                print('\t', count, ': ', key['title'], sep= '')
                print('\t  ', key['price'])
        print('\n' + commands)
        ui = input("Type the corresponding number to remove an item or enter a command:\n")
        menu_option(ui, True)
        try:
            ui = int(ui)
            if ui < 1:
                raise Exception
            product = tmp_list[ui-1][1]
        except:
            print("\nERROR: Invalid number or command.\n")
            continue
        sure = input("\nAre you sure you want to delete {}? (y/n):\n".format(product))
        if sure.lower() == 'y':
            del trackers[tmp_list[ui-1][0]][tmp_list[ui-1][2]]
            update_json(trackers)
            print("\nProduct successfully removed.\n")
        elif sure.lower() == 'n':
            print('\nOkay! Try again!\n')
        else:
            menu_option(sure, True)
            print('\nERROR: Invalid command.\n')
            

if __name__ == '__main__':
# initialize json file
    trackers = {'amazon.com':[], 'target.com':[], 'bestbuy.com': []}
    try:
        with open('tracker.json') as file:
            trackers = json.load(file)
    except:
        update_json(trackers)
# initialize interface
    commands = """********************
COMMANDS:
p: Add products
v: View products
r: Remove products
t: Track price
e: Email testing
h: Help
q: Quit app
********************
"""
    if any([len(trackers[i]) > 0 in trackers[i] for i in trackers]):
        #menu_tracker()
        welcome()
    else:
        welcome()


# You must press the enter/return key to execute any commands or user inputs.  

# This page will print the first time you launch the app.  To see it again just type 'h' or 'help' and then press the enter/return key

# Add products mode allows you to input the URLs of products you want to track.  To enter this mode type 'p'.

# Remove products mode allows you to remove previously added products you no longer want to track.  Type 'r' to enter this mode.

# Track price mode scrapes your product URLs twice daily and will email you if a price drops.
# This is the default mode once products have been added.  This app has to be open and running 24/7 if this mode is active.
# To manually enter this mode after edits type 't'

# Email testing mode allows you to test that emails are working correctly by manually overriding a product price with a higher price.  
# The app will think the price has dropped and send an email.  Once you exit, the product will reset to originally recorded price.
# A local SMTP server must be running to test this feature.  Copy/paste the command below in a seperate terminal/command prompt session.  

# python3 -m smtpd -c DebuggingServer -n localhost:1025 (you'll need to use sudo on Mac or Linux)

# To quit the app completely from any screen type 'q'.