# Notes:
# No error checking for trackers.json being moved or deleted
# Amazon may not work

# import libraries
import smtplib
import json
#import time
import requests
from random import choice
from re import search
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


# whether or not trackers are saved
def trackers_saved(trackers):
    if any([len(trackers[i]) > 0 for i in trackers]):
        return True


# update json file
def update_json(trackers, file = 'tracker.json'):
    with open(file, 'w') as f:
        json.dump(trackers, f, indent = 4)


# spoof browser session
def get_session(url):
    # target.com is rendered with javascript so it requires a different method for scraping.
    if "target.com" in url:
        s = HTMLSession()
        page = s.get(url)
        page.html.render(sleep=1)
    else:
        # this method is faster than the method used for target.  also best buy scaping would not work with the other method.
        # amazon.com has anti-scraping features so a random header is chosen for each request to make it appear as though a
        # different browser is making each request.
        with open('headers.json') as file:
            data = json.load(file)
        header = data[choice(list(data.keys()))] # random header picker
        r = requests.Session()
        response = r.get(url, headers = header)
        page = BeautifulSoup(response.content, 'lxml')
    return page

        
# web scraper
def scrape(url):
    http = search('^https:\/\/www.(bestbuy.com|amazon.com|target.com)', url[:25])  # only need to search beginning of url string
    if http:
        retailer = url[url.find('.')+1:url.find('.com')] + '.com'
        print("\nProcessing...")
        page = get_session(url)
        dict = {'title': '', 'price': '', 'url': url}
        try:
            if "target.com" in url:
                price = page.html.xpath('/html/body/div[1]/div/div[5]/div/div[2]/div[2]/div[1]/div[1]/div[1]', first = True).text.strip()
                dict['title'] = page.html.xpath('/html/body/div[1]/div/div[5]/div/div[1]/div[2]/h1/span', first = True).text.strip()
            elif "amazon.com" in url:
                price = page.find(id="priceblock_ourprice").get_text() # regular price
                if price == None: # if regular price fails, try sale price
                    price = page.find(id="priceblock_dealprice").get_text() # sale price
                dict['title'] = page.find(id="productTitle").get_text().strip()
            elif "bestbuy.com" in url:
                price = page.find(attrs = {'class':'priceView-hero-price priceView-customer-price'}).span.get_text()
                dict['title'] = page.find(attrs = {'class':'sku-title'}).get_text()
            dict['price'] = float(price[1:])
            trackers[retailer].append(dict)
            update_json(trackers)
            r = "Tracker successfully added for {}".format(retailer)
        except:
            r = 'ERROR:\nThe URL is either not a product page or the scrape attempt failed due to technical issues'
    else:
        r = 'ERROR:\nNot a valid command or URL.\nNeeds to be a command from the list below or a complete URL including "http(s)://" and from compatible retailer.'
    return r


# check if user input is an app command
def commands(ui):
    ui = ui.lower()
    h = search("^h\((.*)\)$",ui)
    if ui == 'q':
        exit()
    elif ui == 'h':
        r = command_h(ui)
    elif h:
        r = command_h(ui[2])
    elif ui == 'a':
        command_a()
    elif ui == 'r':
        if trackers_saved(trackers):
            command_r()
        else:
            r = "\nERROR: There are no product pages being tracked.  Add at least one product to enter this mode.\n"
    else:
        r = 'invalid'
    return r


# pretty prints trackers.json data and creates list for data removal
def list_trackers():
    count = 0
    tmp_list = []
    for retailer in trackers:
        tracker_count = 0
        print(retailer + ':')
        for key in trackers[retailer]:
            count += 1
            # this list is used in the command_r() function to map the user input to the trackers.json file
            tmp_list.append([retailer, key['title'], tracker_count])
            tracker_count += 1
            print('\t', count, ': ', key['title'], sep= '')
            print('\t  ', key['price'])
    print('\n')
    return tmp_list


# interface for adding products to json
def command_a(start = False):
    system('clear')
    if start:
        print(welcome)
    while True:
        if trackers_saved(trackers):
            list_trackers()
        print(command_list)
        while True:
            ui = input("Copy/paste the complete URL from a product page to track or enter a command:\n")
            r = commands(ui)
            if r == 'invalid':
                break
            else:
                print(r)
        r = scrape(ui)
        print('\n' + r + '\n')
        # add help suggestion somewhere
        # Type h(a) and press enter/return for help.\n
        
            
# interface for removing products from json
def command_r():
    system('clear')
    while True:
        if trackers_saved(trackers):
            tmp_list = list_trackers()
        else:
            command_a() # switches back to default mode of all trackers are removed
        print(command_list)
        while True:
            ui = input("Type the corresponding number to remove an item or enter a command:\n")
            r = commands(ui)
            if r == 'invalid':
                try:
                    ui = int(ui)
                    if ui < 1:
                        raise Exception
                    product = tmp_list[ui-1][1]
                    break
                except:
                    print("\nERROR:\nNot a valid command or number option. Needs to be a command from the list below or a number from the list above.\n")
                    continue
            else:
                print(r)
                continue
        while True:
            sure = input("\nAre you sure you want to delete {}? (y/n):\n".format(product))
            if sure.lower() == 'y':
                del trackers[tmp_list[ui-1][0]][tmp_list[ui-1][2]]
                update_json(trackers)
                print("\nProduct successfully removed.\n")
                break
            elif sure.lower() == 'n':
                print('\nNo products were removed\n')
                break
            else:
                print('\nERROR:\nChoose yes or no. Type the letter y or the letter n and press enter/return.  No other commands are valid\n')
            

def command_h(command):
    if command == 'a':
        r = """
Type the letter a and press enter/return to enter this mode.  Copy/paste a complete URL (including "http(s)://) from a product page from Amazon, Target, or Best Buy.  
No other retailers will work. Must be a product page.  List pages and search results will not work. 
Press enter and the app will check that the URL is valid.  If so, the app scrapes the webpage, finds the price, and stores the details in the trackers.json file.
This is the default mode the apps enters when started if there are no trackers in the trackers.json file
    """
    elif command == 'r':
        r = """
Type the letter r and press enter/return to enter this mode.  Products are presented in a numbered list. Enter the number of the product you want to remove. 
App removes product from the trackers.json file.  There must me products saved in the trackers.json file to enter this mode. 
        """
    elif command == 't':
        r = """
Type the letter t and press enter/return to enter this mode.  App scrapes product URLs twice daily and will email if a price drops.
This is the default mode the app enters when started once products have been added.  This mode must be active 24/7 for tracking.
Reopen this mode with the 't' command or restart the app.
        """
    elif command == 'e':
        r = """
Type the letter e and press enter/return to enter this mode.  App tests that emails are working correctly by manually overriding a product price with a higher price (from user input).   
App will scrape and compare against the false price and trigger an email.  Once exited, the product will reset to originally recorded price.
A local SMTP server must be running to test this feature.  Copy/paste the command below in a seperate terminal/command prompt session.

python3 -m smtpd -c DebuggingServer -n localhost:1025 (use sudo on Mac or Linux)
        """
    elif command == 'q':
        r = "\nType the letter a and press enter/return to enter this mode.  Completely quits and exits the app.\nTracking will not work if app is quit.  For tracking, use command 't'.\n"
    elif command == 'h':
        r = "\nOffers more information about any command in the menu.  The format is h(command), i.e. type h(a) and press return/enter for help with adding products.\n"
    else:
        r = '\nERROR:\nInvalid option for the help command.\n'
    return r


if __name__ == '__main__':
# initialize json file
    trackers = {'amazon.com':[], 'target.com':[], 'bestbuy.com': []}
    try:
        with open('tracker.json') as file:
            trackers = json.load(file)
    except:
        update_json(trackers)

# initialize interface
    welcome = """
**********************************************************************
Price Drop Scraper will monitor the price of chosen products from popular retailers and email if the price drops.
Created by Wesley Cox
**********************************************************************
"""
    command_list = """/// COMMANDS ///////////////
    a: Add products
    r: Remove products
    t: Track price
    e: Email testing
    h: Help
    q: Quit app
////////////////////////////
""" 
    
    #if trackers_saved(trackers):
    # if any([len(trackers[i]) > 0 in trackers[i] for i in trackers]):
    #     #command_t()
    #     command_a()
    # else:
    command_a(True)