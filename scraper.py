# import libraries
import smtplib
import json
import time
import requests
import re
import os
from random import choice
from bs4 import BeautifulSoup
from selenium import webdriver


# notification email
def send_mail(message):
    sender = 'from@fromdomain.com'
    receivers = ['to@todomain.com']
    message = ( 
        "From: From Person <from@fromdomain.com>\n"
        "To: To Person <to@todomain.com>\n"
        "Subject: A price has dropped for one of your tracked products\n"
        "{}.\n".format(message)
    )
    try:
        smtpObj = smtplib.SMTP('localhost', 1025)
        smtpObj.sendmail(sender, receivers, message)         
        r = "    Successfully sent email.\n"
    except:
        r = error_header + "    Email was not sent.  Make sure to follow the instructions in Help to launch a debugging SMTP server.\n"
    return r


# update json file
def update_json(trackers, file = 'tracker.json'):
    with open(file, 'w') as f:
        json.dump(trackers, f, indent = 4)


# initiate browser session and retrieve and return webpage data
def get_session(url):
    if "bestbuy.com" in url: # beautifulsoup is faster and headless so I prefer this method for compatible websites
        with open('headers.json') as file:
            data = json.load(file)
        header = data[choice(list(data.keys()))] # random header picker -- originally used as a clever way to prevent amazon blocking scrape, but that no longer works so I switched to Selenium
        r = requests.Session()
        response = r.get(url, headers = header)
        page = BeautifulSoup(response.content, 'html.parser')
    else: # selenium is used for target and amazon
        PATH = os.getcwd() + driver
        page = webdriver.Chrome(PATH)
        page.get(url)
    return page


# builds the different messages printed to screen for each command
def start_msg(command, message, quit = False):
    os.system(clear)
    c = command
    m = message   
    arrow_a = ''
    arrow_v = ''
    arrow_t = ''    
    arrow_q = '' 
    print(
        "///// PRICE DROP SCRAPER ///////\n"
        "    Monitors the price of chosen products from popular retailers and emails if the price drops.\n"
        "    Created by Wesley Cox for Code Louisville 2020 Python"
    )
    retailer_list = (
        "\n///// RETAILERS ////////////////\n"
        "    amazon.com\n"
        "    bestbuy.com\n"
        "    target.com\n"
    )
    if c in ('v', 't'): # this block 
        if any([len(trackers[i]) > 0 for i in trackers]): # if any products are saved we want to list them and save them for later.
            m = list_trackers(c) + m
            if c == 'v':
                arrow_v = "  <--"
            if c == 't':
                print(
                    "\n///// IMPORTANT ////////////////\n"
                    "    The intent of this command is to check all saved product pages every 43200 seconds (12 hours),\n"
                    "    compare saved price with current price, and send an email if the price has dropped.\n"
                    "    However, this is a proof-of-concept demonstration.  This app is not currently setup to actually track persistently or send emails.\n"
                    "    This command simply allows testing of those functions.  Type h and press enter/return for more details.\n"
                )
                arrow_t = "  <--"
        else:   # if no products are saved we want to block v and t commands.
            c = 'a'
            arrow_a = "  <--"
            m = alert_header + '    There are no product pages being tracked.  Add at least one product to execute "Remove Products" or "Track Price" commands.\n'
    elif c == 'a':
        arrow_a = "  <--"
        m = retailer_list + m
    else:
        arrow_q = "  <--"
    if not quit:
        m = m + ( "\n///// COMMANDS /////////////////\n"
            "    a: Add products" + arrow_a + "\n"
            "    v: View or remove products" + arrow_v + "\n"
            "    t: Track price" + arrow_t + "\n"
            "    h: Help\n"
            "  ^+c: Quit app" + arrow_q + "\n"
        )
    print(m)
    return c
    
        
# web scraper
def scrape(url, update = True):
    http = re.search('^https:\/\/www.(bestbuy.com|amazon.com|target.com)', url[:25])  # only need to search beginning of url string
    if http:
        retailer = url[url.find('.')+1:url.find('.com')] + '.com'
        print('\n' + alert_header + "    Processing...\n")
        try:
            page = get_session(url)
        except:
            r = error_header + '    Configuration issue with Selenium or Beautiful Soup.\n    Make sure they\'re installed and that the "chromedriver" file is saved in the current directory.\n'
        else:
            dict = {'title': '', 'price': '', 'url': url}
            try:
                if "target.com" in url:
                    price = page.find_element_by_xpath('/html/body/div[1]/div/div[5]/div/div[2]/div[2]/div[1]/div[1]/div[1]').text
                    dict['title'] = page.title
                    page.quit()
                elif "amazon.com" in url:
                    try:
                        price = page.find_element_by_id("priceblock_ourprice").text
                    except:
                        price = page.find_element_by_id("priceblock_dealprice").text
                    dict['title'] = page.title
                    page.quit()
                elif "bestbuy.com" in url:
                    with open('bestbuy.json', 'w') as f:
                        json.dump(page, f, indent=4, default=str)
                    price = page.find(attrs = {'class':'priceView-hero-price priceView-customer-price'}).span.get_text()
                    dict['title'] = page.find(attrs = {'class':'sku-title'}).get_text()
                dict['price'] = float(price.replace(',','')[1:])
                if update:
                    trackers[retailer].append(dict)
                    update_json(trackers)
                    r = success_header + "    {} from {} is now being tracked.\n".format(dict['title'], retailer)
                else:
                    r = dict['price']
            except:
                r = error_header + '    Was not able to find a price.  Either the URL is not a product page or product is no longer available.\n    Type h and press enter/return for more details.\n'
    else:
        r = error_header + '    Not a valid command or URL.  Needs to be a command from the list below or a complete URL including "http(s)://" and from compatible retailer.\n    Type h and press enter/return for more details.\n'
    try:
        page.quit()
    except:
        pass
    return r


# periodically scrapes saved urls and sends email if price has dropped
def tracker(ui):
    retailer, title, price, url, tmp = tracker_list[0]
    price_override = price + 10
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
        try:
            new_price = scrape(url, False)
            m = success_header + "    Last scrape: " + str(time.ctime()) + '\n'
            if new_price < price_override:
                drop = '{:.2f}'.format(price_override - new_price)
                msg = "{} from {} dropped by ${}:\n{}".format(title, retailer, drop, url)
                email = send_mail(msg)
                m += f'    Price dropped ${drop}\n' + email
            else:
                m += '    Price did not drop.\n' # this shouldn't ever trigger since we're intentionally making price higher. 
        except:
            m = error_header + "    There was an ERROR processing the URL.  It's possible the product is no longer available or the webpage has changed.\n"
    elif ui == 'n':
        m = alert_header + '    Tracker not started.  You can exit using one of the commands in the menu.\n'
    else:
        m = error_header + '    Invalid command.  Choose yes or no or a valid command from the menu.\n    Type h and press enter return for more details.\n'
    return m


def view(ui):
    try: # need to test that user input was a valid number before we proceed.
        ui = int(ui)
        if ui < 1: # negatives aren't necessarily out of range so we need to catch those. 
            raise Exception
        title = tracker_list[ui-1][1]
    except:
        m =  error_header + "    Not a valid command or number option. Type h(v) and press enter/return for more details.\n"
    else:
        sure = input("\nAre you sure you want to delete {}? (y/n):\n".format(title)).lower()
        if sure == 'y': # delete tracker and update json
            del trackers[tracker_list[ui-1][0]][tracker_list[ui-1][4]]
            update_json(trackers)
            m = success_header + "    Product successfully removed.\n"
        else:
            m = alert_header + '    No products were removed.\n'
    return m


# checks to see if user input is a command rather than an option
def command_menu(ui, command):
    ui = ui.lower()
    h = re.search("^h\((.*)\)$", ui) 
    if ui == 'h':
        r = help(command, True)
    elif h:
        opt = h.groups()[0]
        r = help(opt)
    elif ui == '^+c':
        r == help(ui)
    elif ui in ('a', 'v', 't'):
        r = 'command'
    else:
        r = 'option'
    return r


# pretty prints trackers.json data and creates list for data removal
def list_trackers(command):
    c = command
    count = 0
    m = ''
    for retailer in trackers:
        tracker_count = 0
        if len(trackers[retailer]) > 0:
            m += '    ' + retailer + ':\n'
        for key in trackers[retailer]:
            count += 1
            tracker_list.append([retailer, key['title'], key['price'], key['url'], tracker_count])
            tracker_count += 1
            m += '\t' + str(count) + ': ' + key['title'] + '\n'
            m += '\t   $' + format(key['price'], '.2f') + '\n'
    if c == 'v':
        m = "\n///// TRACKED PRODUCTS //////////\n" + m
    if c == 't':
        m = (
            "///// TRACKED PRODUCT SAMPLE ////\n" + '    ' +
            tracker_list[0][1] + '\n' +
            "    $" + '{:.2f}'.format(tracker_list[0][2]) +
            "\n\n///// PRICE OVERRIDE ////////////\n" +
            "    $" + '{:.2f}'.format(tracker_list[0][2] + 10) + '\n'
        )
    return m        


def quit():
    try:
        m = ''
        c = '^+c'
        while True:
            start_msg(c, m)
            ui = input('Do you want to completely exit app and stop tracking (y) or choose a different command?: ').lower()
            if ui == 'y':
                m = alert_header + '    App was closed and is no longer tracking product price changes.'
                start_msg(c, m, True)
                break # end loop and app stops running
            else:
                r = command_menu(ui, '^+c')
                if r == 'command':
                    break # end loop and call commands() to restart with new user input
                elif r == 'option':
                    m = error_header + '    Invalid command.  Please type the letter y and press enter/return or choose a command from the menu.\n'
                else:
                    m = r
        if ui != 'y':
            commands(ui) # restarts app with new command
    except KeyboardInterrupt:
        m = alert_header + '    App was forced closed and is no longer tracking product price changes.'
        start_msg(c, m, True)


# user interface:
def commands(command, message = ''):
    c = command
    m = message
    try:
        while True:
            c = start_msg(c, m) # checks if any trackers are saved, resets c if not,  and prints appropriate messages to the screen.
            if c == 'a':    # different inputs for each command
                ui = input("Copy/paste the complete URL from a product page to track or enter a command: ")
            if c == 'v':
                ui = input("Type the corresponding number to remove an item or enter a command: ")
            if c == 't':
                ui = input('Are you ready to test tracker and email? (y/n): ')
            r = command_menu(ui, c) # check if input is an attempt to change commands, get help, or argument for current command.
            if r == 'option': # this means the input was not a help request or different command so it might be a valid option or argument for this command's functions.
                if c == 'a':
                    m = scrape(ui) # this method checks that input is valid URL, then scrapes for price, then returns success or errors.
                if c == 'v':
                    m = view(ui) # lists and numbers are products being tracked and gives option to remove one.
                if c == 't':
                    m = tracker(ui) # picks 1 product from tracker.json, overrides the price with higher amount, scrapes webpage again, checks if price is lower, and sends test email if it is.
            elif r == 'command': 
                c = ui.lower()
                m = ''
            else: # this means input was help request and simply prints that data to screen.  
                m = r
    except KeyboardInterrupt:
        quit()


# help requests
def help(command, h = False):
    tail = ''
    if h:
        tail = '\n    You can get help for inactive commands by typing h(command), i.e. h(^+c) for help with "Quit app" or h(a) for help with "Add products."\n'
    if command == 'a':
        r = (
            '    Copy/paste a complete URL (including "http(s)://") from a product page from Amazon, Target, or Best Buy.\n'
            "    No other retailers will work. Must be a product page.  List pages and search results will not work.\n"
            "    Product page must have a price listed.  Pre-orders and out-of-stock items might not be compatible.\n"
            "    Press enter and the app will check that the URL is valid.  If so, the app scrapes the URL, finds the price,\n"
            "    and stores the details in the tracker.json file.  This is the default command for the app.\n" + tail
        )
    elif command == 'v':
        r = (
            "    To remove a product from the list enter the corresponding number of the product to be removed and press enter/return.\n"
            "    The product will be deleted from the tracker.json file.  This command requires at least 1 product to be saved in the tracker.json file.\n" 
            '    Will automatically switch to the default command of "Add products" if there are not products being tracked.\n' + tail
        )
    elif command == 't':
        r = (
            "    Manually overrides 1 saved product's price with a higher price.  30 seconds later the app will scrape the URL again,\n"
            "    compare the current price with the higher override price, print a confirmation to the screen and then send a test email.\n"
            "    To test the email functionality a local SMTP server must be running.\n"
            "    Copy/paste the command below in a seperate terminal/command prompt session.\n\n"
            "    python3 -m smtpd -c DebuggingServer -n localhost:1025\n\n"
            "    If the server is not running, all the other steps will still take place as described above.\n"
            "    There must be saved products in the tracker.json file to execute this command.\n"
            "    Once you are tracking, you must press the control key and the letter c key (^+c) to exit.  All other commands are ignored.\n" + tail
        )
    elif command == '^+c':
        r = "    ^+c represents a key combination and not literal characters.  Press the control key and the letter c key at the same time.\n    Gives you the option to completely quit and exit app.  Tracking will not work if app is quit.  For tracking, use command 't'.\n" + tail
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

# os dependencies
    if os.name == 'posix':
        clear = 'clear'
        driver = '/chromedriver'
    else:
        clear =  'cls'
        driver = '\\chromedriver'

# globals
    tracker_list = []
    error_header = "\n///// ERROR ////////////////////\n"
    success_header = "\n///// SUCCESS //////////////////\n"
    alert_header = "\n///// ALERT ////////////////////\n"
    
# initialize interface
    commands('a')