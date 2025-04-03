import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

r_clean = re.compile(r'[^\d,]+')

options = Options()
options.add_argument('--headless')  # běží bez GUI
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

from_iata = 'VIE'
to_iata = 'TFS'
departure_date = '2025-04-03'
return_date = '2025-04-07'


url = f'https://www.ryanair.com/cz/cs/booking/home/{from_iata}/{to_iata}/{departure_date}/{return_date}/1/0/0/null'
driver.get(url)

time.sleep(5)

try:
    # test if there is departure element
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f'//button[@data-ref="{departure_date}"]'))
    )

    print("Loaded...")

    dprice = None
    rprice = None

    departure_price = driver.find_elements(By.XPATH, f'//button[@data-ref="{departure_date}"]/div[contains(@class, "date-item__price")]')
    if departure_price:
        dprice = float(r_clean.sub('', departure_price[0].text).replace(',', '.'))
        print(dprice)

    return_price = driver.find_elements(By.XPATH, f'//button[@data-ref="{return_date}"]/div[contains(@class, "date-item__price")]')
    if return_price:
        rprice = float(r_clean.sub('', return_price[0].text).replace(',', '.'))
        print(rprice)
    
    price = dprice + rprice

    print(f'Price of flight from {from_iata} to {to_iata} on {departure_date} and return on {return_date} is {price} EUR.')

except Exception as e:
    print("Chyba při získávání dat:", e)

driver.quit()