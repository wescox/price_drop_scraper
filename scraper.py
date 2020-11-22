# must start a local debugging smtp server by executing the below command in a terminal shell
# sudo python3 -m smtpd -c DebuggingServer -n localhost:1025

# libraries
import smtplib
from requests_html import HTMLSession
from pyppdf import patch_pyppeteer

# send email
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


url = "https://www.target.com/p/delta-children-adley-3-in-1-convertible-crib/-/A-53618889?preselect=75003678#lnk=sametab"
s = HTMLSession()
content = s.get(url)
content.html.render(sleep=1)
price = content.html.xpath('/html/body/div[1]/div/div[5]/div/div[2]/div[2]/div[1]/div[1]/div[1]', first = True).text

print(price)

url = "https://www.amazon.com/eufy-Security-Monitor-Display-Wide-Angle-dp-B07YD8W5B9/dp/B07YD8W5B9/ref=dp_ob_title_baby"
s = HTMLSession()
content = s.get(url)
content.html.render(sleep=1)
price = content.html.xpath('//*[@id="priceblock_ourprice"]', first = True).text

print(price)

#headers  = {
#    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:82.0) Gecko/20100101 Firefox/82.0"
#}
#page = requests.get(URL, headers=headers)
#content = BeautifulSoup(page.content, 'html.parser')
#price = content.find(id="priceblock_ourprice")
#print(content)