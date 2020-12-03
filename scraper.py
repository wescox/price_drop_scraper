# import libraries
import smtplib
import json
import time
import requests
import re
from random import choice
from datetime import datetime
from os import system
from requests_html import HTMLSession
from pyppdf import patch_pyppeteer #only needed for Mac
from bs4 import BeautifulSoup


# notification email
def send_mail(message):
    sender = 'from@fromdomain.com'
    receivers = ['to@todomain.com']
    message = ( 
        "From: From Person <from@fromdomain.com>\n"
        "To: To Person <to@todomain.com>\n"
        "Subject: A price has dropped for one of your tracked products\n\n"
        "{}.\n\n".format(message)
    )
    try:
        smtpObj = smtplib.SMTP('localhost', 1025)
        smtpObj.sendmail(sender, receivers, message)         
        r = "    Successfully sent email.\n"
    except:
        r = error_header + "    Email was not sent.  Make sure to follow the instructions in Help to launch a debugging SMTP server.\n"
    return r


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
    if "target.com" in url: # target.com is rendered with javascript so it requires a different method for scraping.
        s = HTMLSession()
        page = s.get(url)
        page.html.render(sleep=1)
    else:
        with open('headers.json') as file:
            data = json.load(file)
        header = data[choice(list(data.keys()))] # random header picker
        r = requests.Session()
        response = r.get(url, headers = header)
        page = BeautifulSoup(response.content, 'lxml')
    return page

        
# web scraper
def scrape(url, update = True):
    http = re.search('^https:\/\/www.(bestbuy.com|amazon.com|target.com)', url[:25])  # only need to search beginning of url string
    if http:
        retailer = url[url.find('.')+1:url.find('.com')] + '.com'
        print('\n' + alert_header + "    Processing...\n")
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
            if update:
                trackers[retailer].append(dict)
                update_json(trackers)
                r = success_header + "    {} from {} is now being tracked.\n".format(dict['title'], retailer)
            else:
                r = dict['price']
        except:
            r = error_header + '    The URL is either not a product page or the scrape attempt failed due to technical issues.\n    Type h(a) and press enter/return for more details.\n'
    else:
        r = error_header + '    Not a valid command or URL.  Needs to be a command from the list below or a complete URL including "http(s)://" and from compatible retailer.\n    Type h(a) and press enter/return for more details.\n'
    return r


# starts app with ability to catch ^+c. added mainly to avoid a ton of recursion. 
def launch(command, message = ''):
    try:
        commands(command, message)
    except KeyboardInterrupt:
        quit_app()


def quit_app(message = ''):
    try:
        system('clear')
        m = message
        command_list = (
            "\n///// COMMANDS /////////////////\n"
            "    a: Add products\n"
            "    v: View or remove products\n"
            "    t: Track price\n"
            "    h: Help\n"
            "  ^+c: Quit app  <--\n"
        )
        print(app_title + m + command_list)
        ui = input('Do you want to completely exit app and stop tracking (y) or choose a different command?: ').lower()
        if ui == 'y':
            system('clear')
            print(app_title)
            print(alert_header[1:] + '    App was closed and is no longer tracking product price changes.')
        else:
            r = command_menu(ui, '^+c')
            if r == 'command':
                launch(ui) # restarts app with new command
            elif r == 'option':
                m = error_header + '    Invalid command.  Please type the letter y and press enter/return or choose a command from the menu.\n'
            else:
                m = r
            quit_app(m)
    except KeyboardInterrupt:
        system('clear')
        print(app_title)
        print(alert_header[1:] + '    App was forced closed and is no longer tracking product price changes.')


# checks to see if user input is a command rather than an option
def command_menu(ui, command):
    h = re.search("^h\((.*)\)$",ui) 
    if ui == 'h':
        r = help(command, True)
    elif h:
        opt = h.groups()[0]
        r = help(opt)
    elif ui in ('a', 'v', 't'):
        r = 'command'
    else:
        r = 'option'
    return r


# pretty prints trackers.json data and creates list for data removal
def list_trackers():
    count = 0
    tmp_list = []
    m = "///// TRACKED PRODUCTS //////////\n"
    for retailer in trackers:
        tracker_count = 0
        if len(trackers[retailer]) > 0:
            m += '    ' + retailer + ':\n'
        for key in trackers[retailer]:
            count += 1
            tmp_list.append([retailer, key['title'], key['price'], key['url'], tracker_count])
            tracker_count += 1
            m += '\t' + str(count) + ': ' + key['title'] + '\n'
            m += '\t   $' + format(key['price'], '.2f') + '\n'
    return tmp_list, m        
            

# user interface:
def commands(command, message):
    system('clear')
    c = command
    m = message
    arrow_a = ''
    arrow_v = ''
    arrow_t = ''
    print(app_title)
    if c in ('v', 't'): # if any products are saved we want to list them and save them for later.
        if trackers_saved(trackers):
            tmp_list, tracker_m = list_trackers()
            if c == 'v':
                arrow_v = "  <--"
                m = tracker_m + m
            if c == 't': # building the message to print for this command
                arrow_t = "  <--"
                retailer, title, price, url, tmp = tmp_list[0]
                price_override = price + 10
                m = (
                    help('t')[1:] + '\n' +
                    "///// TRACKED PRODUCT SAMPLE ////\n" + '    ' +
                    title + '\n' +
                    "    $" + '{:.2f}'.format(price) + '\n\n' +
                    "///// PRICE OVERRIDE ////////////\n" +
                    "    $" + '{:.2f}'.format(price_override) + '\n' + m
                )
        else:   # if no products are saved we want to block v and t commands. 
            error = alert_header + '    There are no product pages being tracked.  Add at least one product to execute "Remove Products" or "Track Price" commands.\n'
            launch('a', error) # switches back to default command if all products are removed from tracking.
    else:
        arrow_a = "  <--"
        m = retailer_list + m
    command_list = (
        "///// COMMANDS /////////////////\n"
        "    a: Add products" + arrow_a + "\n"
        "    v: View or remove products" + arrow_v + "\n"
        "    t: Track price" + arrow_t + "\n"
        "    h: Help\n"
        "  ^+c: Quit app\n"
    )
    print(m)
    print(command_list)
    if c == 'a':    # different inputs for each command
        ui = input("Copy/paste the complete URL from a product page to track or enter a command: ").lower()
    if c == 'v':
        ui = input("Type the corresponding number to remove an item or enter a command: ").lower()
    if c == 't':
        ui = input('Are you ready to test tracker and email? (y/n): ').lower()
    r = command_menu(ui, c) # check if input is an attempt to change commands, get help, or argument for current command.
    if r == 'option': # this means the input was not a help request or different command so it might be a valid option or argument for this command's functions.
        if c == 'a':
            m = scrape(ui) # this method checks that input is valid URL, then scrapes for price, then returns success or errors.
        if c == 'v':
            error = False
            try: # need to test that user input was a valid number before we proceed.
                ui = int(ui)
                if ui < 1: # negatives aren't necessarily out of range so we need to catch those. 
                    raise Exception
                title = tmp_list[ui-1][1]
            except:
                m =  error_header + "    Not a valid command or number option. Type h(v) and press enter/return for more details.\n"
                error = True
            if not error:
                sure = input("\nAre you sure you want to delete {}? (y/n):\n".format(title)).lower()
                if sure == 'y': # delete tracker and update json
                    del trackers[tmp_list[ui-1][0]][tmp_list[ui-1][4]]
                    update_json(trackers)
                    m = success_header + "    Product successfully removed.\n"
                elif sure == 'n':
                    m = alert_header + '    No products were removed.\n'
                else:
                    m = error_header + '    Choose yes or no. Type the letter y or the letter n and press enter/return.  No other commands or input are valid.\n'
        if c == 't':
            if ui == 'y':
                t = 30
                print('\n///// WAITING //////////////////')
                while t > 10:
                    print('   ', str(t), 'seconds...')
                    t -= 10
                    time.sleep(10)
                while t > 0:
                    if t == 1:
                        print('   ', str(t), 'second...')
                    else:
                        print('   ', str(t), 'seconds...')
                    t -= 1
                    time.sleep(1)
                new_price = scrape(url, False) # we're assuming this will work since it worked previously.  there should probably be an error catch. 
                m = '\n' + success_header + "    Last scrape: " + str(datetime.now()) + '\n'
                if new_price < price_override:
                    drop = '{:.2f}'.format(price_override - new_price)
                    msg = "{} from {} dropped by ${}:\n{}".format(title, retailer, drop, url)
                    email = send_mail(msg)
                    m += f'    Price dropped ${drop}\n' + email
                else:
                    m += '    Price did not drop.\n' # this should actually ever trigger. 
            elif ui == 'n':
                m = alert_header + '    Tracker not started.  You can exit using one of the commands in the menu.\n'
            else:
                m = error_header + '    Invalid command.  Choose yes or no or a valid command from the menu.\n    Type h(t) and press enter return for more details.\n'
    elif r == 'command': # help is printed, then help loop starts over to print the same input option again.
        c = ui
        m = ''
    else:
        m = r
    launch(c, m)


# help requests
def help(command, h = False):
    tail = ''
    if h:
        tail = '\n    You can get help for inactive commands by typing h(command), i.e. h(^+c) for help with "Quit app" or h(a) for help with "Add products"\n'
    if command == 'a':
        r = (
            '    Type the letter a and press enter/return to execute this command.  Copy/paste a complete URL (including "http(s)://) from a product page from Amazon, Target, or Best Buy.\n'
            "    No other retailers will work. Must be a product page.  List pages and search results will not work.\n"
            "    Product page must have a price listed.  Pre-orders and out-of-stock items might not be compatible.\n"
            "    Press enter and the app will check that the URL is valid.  If so, the app scrapes the webpage, finds the price, and stores the details in the trackers.json file.\n"
            "    This is the default command for the app when launched.\n" + tail
        )
    elif command == 'v':
        r = (
            "    Type the letter v and press enter/return to execute this command.  Products are presented in a numbered list\n."
            "    To remove a product from the list enter the corresponding number of the product to be removed and press enter/return.\n"
            "    The product will be deleted from the trackers.json file.  This command requires at least 1 product to be saved in the trackers.json file.\n" 
            '    If all products are removed, app will switch to the default command of "Add products".\n' + tail
        )
    elif command == 't':
        r = (
            "    The app is a proof-of-concept demonstration.  It's not setup to actually track persistently or send emails.  This command simply allows testing of those functions.\n" 
            "    It will manually override a saved product's price with a higher price.  30 seconds later, the app will scrape the URL again, find the lower price, print a\n"
            "    confirmation to the screen, and then send an email. To test the email functionality a local SMTP server must be running.\n"
            "    Copy/paste the command below in a seperate terminal/command prompt session.\n\n"
            "    python3 -m smtpd -c DebuggingServer -n localhost:1025 (use sudo on Mac or Linux)\n\n"
            "    If the server is not running, all the other steps will still take place as described above.\n"
            "    There must be saved products in the trackers.json file to execute this command.\n"
            "    Once you are tracking, you must press the control + C to exit.  The other commands will not work.\n" + tail
        )
    elif command == '^+c':
        r = "    This is shorthand for pressing the control key and letter c at the same time.\n    Gives you the option to completely quit and exit app.\n    Tracking will not work if app is quit.\n    For tracking, use command 't'.\n" + tail
    else:
        r = "    Invalid option for the help command. Type h and press return/enter for more details\n" + tail
    return "\n///// HELP /////////////////////\n" + r


if __name__ == '__main__':
# initialize json file
    trackers = {'amazon.com':[], 'target.com':[], 'bestbuy.com': []}
    try:
        with open('tracker.json') as file:
            trackers = json.load(file)
    except:
        update_json(trackers)

# initialize interface
    app_title = (
        "///// PRICE DROP SCRAPER ///////\n"
        "    Monitors the price of chosen products from popular retailers and emails if the price drops.\n"
        "    Created by Wesley Cox for Code Louisville 2020 Python\n"
    )
    retailer_list = (
        "///// RETAILERS ////////////////\n"
        "    amazon.com\n"
        "    bestbuy.com\n"
        "    target.com\n"
    )
    error_header = "\n///// ERROR ////////////////////\n"
    success_header = "\n///// SUCCESS //////////////////\n"
    alert_header = "\n///// ALERT ////////////////////\n"
    launch('a')