import time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def load_secret(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        line = f.readline().strip()
        netid, passwd, otp = line.split()
        return netid, passwd, otp
    
def wait_and_send_keys(waiter, selector_type, selector, payload):
    waiter.until(EC.element_to_be_clickable((selector_type, selector))).send_keys(payload)

def wait_and_click(waiter, wait_func, selector_type, selector):
    waiter.until(wait_func((selector_type, selector))).click()


def goto_login_page(wait, driver):
    wait_and_click(wait, EC.element_to_be_clickable, By.CSS_SELECTOR, 'div.item[data-id=DU_HPT_CX_SHIB_LOGIN]')
    wait_and_click(wait, EC.element_to_be_clickable, By.ID, 'expand-netid')


def do_login(wait, driver, netid, passwd, otp):
    # handle netid login and 2FA
    wait_and_send_keys(wait, By.ID, 'j_username', netid)
    
    passwd_field = driver.find_element(By.CSS_SELECTOR, '#j_password')
    passwd_field.click()
    passwd_field.send_keys(passwd)
    
    wait.until(EC.visibility_of_element_located((By.ID, 'duoPasscodeInput')))
    driver.find_element(By.CSS_SELECTOR, '#rememberme').click()
    driver.find_element(By.CSS_SELECTOR, '#duoPasscodeInput').send_keys(otp)
    driver.find_element(By.CSS_SELECTOR, '#Submit').click()
    
    
def checkout(wait, driver):
    # at dukehub homepage, now checkout shopping cart
    school_button_xpath = '/html/body/div[1]/nav/div[2]/div[2]/ul/li[4]/div/button'
    shopping_cart_xpath = '/html/body/div[1]/nav/div[2]/div[2]/ul/li[4]/div/ul/li[4]/a'
    wait.until(EC.element_to_be_clickable((By.XPATH, school_button_xpath))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, shopping_cart_xpath))).click()
    
    # hit enroll button
    enroll_xpath = '/html/body/div[1]/main/div/div/div[3]/div/div[2]/div/div[4]/button'
    wait.until(EC.element_to_be_clickable((By.XPATH, enroll_xpath))).click()
    

def registration():
    netid, passwd, otp = load_secret('secret.txt')
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 20)
        
    driver.get("https://dukehub.duke.edu")
    
    goto_login_page(wait, driver)
    do_login(wait, driver, netid, passwd, otp)
    checkout(wait, driver)
    driver.save_screenshot('result.png')
    time.sleep(10)
    # voila!

if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='America/New_York')
    trigger = CronTrigger(hour=7, minute=1)
    scheduler.add_job(registration, trigger)
    try:
        scheduler.start()
    except (KeyboardInterrupt):
        scheduler.shutdown(wait=False)
