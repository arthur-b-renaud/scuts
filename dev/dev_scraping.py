from scuts.scraping import CustomDriver
from time import sleep
import os.path as op
import os

driver = CustomDriver()
# driver.get_with_proxy('https://api.ipify.org?format=json')

# init if necessary
# driver.get('https://www.bws.com.au')
driver.get('https://www.nicolas.fr/')

# sleep(5)# Take screenshot
# driver.waitclick('//*[@class=" NostoOverlayClose  NostoCloseButton"]')
driver.fullpage_screenshot('/tmp/bws.png', verbose=True)
os.system('firefox /tmp/bws.png')
