# must start a local debugging smtp server by executing the below command in a terminal shell
# sudo python3 -m smtpd -c DebuggingServer -n localhost:1025

#https://www.target.com/p/delta-children-adley-3-in-1-convertible-crib/-/A-53618889?preselect=75003678#lnk=sametab
#https://www.amazon.com/eufy-Security-Monitor-Display-Wide-Angle-dp-B07YD8W5B9/dp/B07YD8W5B9/ref=dp_ob_title_baby

# #html = soup.prettify("utf-8")
# # with open("output2.html", "wb") as file:
# #     file.write(html)

# # print trackers to screen - add to interface
# retailer_count = 0
# tmp_list = []
# for retailer in data:
#     retailer_count += 1
#     tmp_list.append(retailer)
#     print(retailer_count, ': ', retailer.capitalize(), ':', sep= '')
#     tracker_count = 0
#     for key in data[retailer]:
#         tracker_count += 1
#         print('\t', tracker_count, ': ', key['title'], sep= '')
#         print('\t  ', key['price'])

# #del data[tmp_list[1]][2]

# TODO: add regex for retailer in scrape

# libraries
import smtplib
import json
import time
import random
import requests
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
        with open('headers.json') as f:
            data = json.load(f)
        headers_list = list(data.keys())
        header = data[random.choice(headers_list)]
        r = requests.Session()
        response = r.get(url, headers = header)
        page = BeautifulSoup(response.content, 'html.parser')
    return page

        
# web scraper
def scrape(url):
    print("\nProcessing...\n")
    page = get_session(url)
    price = ''
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
    update_json(dict, retailer)
    print("{} tracker successfully added".format(retailer))


# update json file
def update_json(dict, retailer, file = 'tracker.json'):
    with open(file) as f:
        data = json.load(f)
    tmp = data[retailer]
    tmp.append(dict)
    with open(file, 'w') as f:
        json.dump(data, f, indent = 4)


if __name__ == '__main__':
    #initialize json file
    retailers_dict = {'amazon.com':[], 'target.com':[], 'bestbuy.com': []}
    try:
        with open('tracker.json') as file:
            pass
    except:
        with open('tracker.json', 'w') as file:
            json.dump(retailers_dict, file, indent = 4)

    # user interface
    print(
"""

Make sure to run the command below in a separate terminal window to initiate a debugging SMTP server:
python3 -m smtpd -c DebuggingServer -n localhost:1025 (you'll need to use sudo on Mac or Linux)

You can track products from these retailers:
Amazon
Target
Best Buy

When you're finished entering URLs, type 'q' and press return to exit. 
"""
    )
    url = ''
    while True:
        url = input("\nWhat's the URL of the product you want to track?\n")
        if url.lower() in ('q', 'quit', 'exit', 'stop'):
            break
        else:
            try:
            #if any([i in url for i in list(retailers_dict.keys())]):
                scrape(url)
            except:
                print("\nERROR: That's not a compatible URL.")