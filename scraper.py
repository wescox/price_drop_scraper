# must start a local debugging smtp server by executing the below command in a terminal shell
# sudo python3 -m smtpd -c DebuggingServer -n localhost:1025

# libraries
import smtplib
from requests_html import HTMLSession
from pyppdf import patch_pyppeteer


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
    except SMTPException:
        print("Error: unable to send email")


# web scraper
def get_price(url):
    s = HTMLSession()
    content = s.get(url)
    content.html.render(sleep=1)
    if "target" in url:
        price = content.html.xpath('/html/body/div[1]/div/div[5]/div/div[2]/div[2]/div[1]/div[1]/div[1]', first = True).text
    if "amazon" in url:
        price = content.html.xpath('//*[@id="priceblock_ourprice"]', first = True).text
    return price


# user interface
url = input(
"""

**********
quit = q
**********

What's the URL of the product you want to track on Target?
"""
)
print("\n\n" +  get_price(url) + "\n")

#https://www.target.com/p/delta-children-adley-3-in-1-convertible-crib/-/A-53618889?preselect=75003678#lnk=sametab
#https://www.amazon.com/eufy-Security-Monitor-Display-Wide-Angle-dp-B07YD8W5B9/dp/B07YD8W5B9/ref=dp_ob_title_baby