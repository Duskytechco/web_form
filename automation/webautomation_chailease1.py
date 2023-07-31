from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium_recaptcha_solver import RecaptchaSolver
from time import sleep
import pandas as pd
import re
import os
import random
import requests
import mysql.connector


cnx = mysql.connector.connect(host="149.28.139.83", user='sharedAccount', port='3306', password='Shared536442.', database='crm_002_db')
def get_location_by_postcode(postcode):
    url = f"https://postcode.my/search/?keyword={postcode}&state="
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        # Extract the location from the HTML using regular expressions
        match = re.findall(r'<td[^>]*><strong><a[^>]*>([^<]*)</a>', html)
        match1 = re.search(r'<td[^>]*><strong><a[^>]*>([^<]*)</a>', html)
        if match[1] == 'Wilayah Persekutuan':
            return [f"{match[1]} {match[0]}", match1.group(1)]
        if match and match1:
            return [match[1], match1.group(1)]
    return None


PATH = "/snap/bin/chromium.chromedriver"
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(PATH, options=options)

wait = WebDriverWait(driver, 10)

solver = RecaptchaSolver(driver)

driver.get("https://e-submission.chailease.com.my/")
sleep(random.randint(3, 5))

scroll_amount = random.randint(100, 500)
driver.execute_script(
    "window.scrollTo(0, " + str(scroll_amount) + ");")
sleep(random.randint(1, 3))

username = "MKUL0015"
password = "Motosing1963@"

# Username and Password
driver.find_element(By.XPATH, "//*[@id='account']").send_keys(username)
driver.find_element(
    By.XPATH, "//*[@id='userPassword']").send_keys(password)
sleep(1)

# Im not a robot reCaptcha
# iframe = driver.find_element(By.XPATH,"/html/body/app-root/div[1]/app-login/div/main/div/div[2]/form/div[4]/re-captcha/div/div/iframe")
# driver.switch_to.frame(iframe)
# driver.find_element(By.XPATH,"/html/body/div[2]/div[3]/div[1]/div/div/span/div[1]").click()
# sleep(1)
# driver.switch_to.default_content()
# sleep(1)

import ffmpeg
import openai


# Log In
driver.find_element(
    By.XPATH, "/html/body/app-root/div[1]/app-login/div/main/div/div[2]/form/div[5]/div/a").click()
sleep(5)

# Submission Button
Submission = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > app-side-menu > p-sidebar.ng-tns-c33-12.ng-star-inserted > div > div > div > ul > li:nth-child(1) > a').click()"
driver.execute_script(Submission)
while True:
    try:

        # FOR LINUX
        # data = pd.read_excel(r"/home/Sing/Coding/Work/Loan_App_2023.xlsx", dtype=str)
        # data = data.dropna(how='all').head(n=-1)
        # print(data)

        # FOR WINDOWS
        # data = pd.read_excel(r"C:\Users\jerwo\AppData\Roaming\Python\Python310\site-packages\selenium\personal-project\Loan_App_2023.xlsx", dtype=str)
        # data = data.dropna(how='all').head(n=-1)
        nric = input('Please insert NRIC for further action : ')
        if nric.lower() == 'exit':
            break
        dfProductInfo = pd.read_sql(
            f"SELECT * FROM `Product Info` WHERE NRIC={nric}", cnx)

        for i in range(0, len(dfProductInfo)):

            # New Case Application
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-leading-page/div[1]/div[1]/p-radiobutton/div/div[2]").click()
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-leading-page/div[1]/div[2]/div/div/p-dropdown/div/span").click()
            product = dfProductInfo['Product Type'].item().split()
            Product = f"{product[0] + product[-1].split(')')[-1]}"

            superbike_new = "/html/body/app-root/div[1]/app-layout/div/div/div/app-leading-page/div[1]/div[2]/div/div/p-dropdown/div/div[3]/div[2]/ul/p-dropdownitem[1]"
            superbike_used = "/html/body/app-root/div[1]/app-layout/div/div/div/app-leading-page/div[1]/div[2]/div/div/p-dropdown/div/div[3]/div[2]/ul/p-dropdownitem[2]"
            moped_new = "/html/body/app-root/div[1]/app-layout/div/div/div/app-leading-page/div[1]/div[2]/div/div/p-dropdown/div/div[3]/div[2]/ul/p-dropdownitem[3]"
            moped_rnm = "/html/body/app-root/div[1]/app-layout/div/div/div/app-leading-page/div[1]/div[2]/div/div/p-dropdown/div/div[3]/div[2]/ul/p-dropdownitem[4]"
            moped_used = "/html/body/app-root/div[1]/app-layout/div/div/div/app-leading-page/div[1]/div[2]/div/div/p-dropdown/div/div[3]/div[2]/ul/p-dropdownitem[5]"

            if Product == "superbikenew":
                driver.find_element(By.XPATH, superbike_new).click()
            elif Product == "superbikeused":
                driver.find_element(By.XPATH, superbike_used).click()
            elif Product == "mopednew":
                driver.find_element(By.XPATH, moped_new).click()
            elif Product == "mopedrnm":
                driver.find_element(By.XPATH, moped_rnm).click()
            elif Product == "mopedused":
                driver.find_element(By.XPATH, moped_used).click()
            sleep(2)

            # Next Button
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-leading-page/div[2]/a").click()
            sleep(8.5)

            # Page 1/7 Customer Infomation
            # ID No.(IC)
            data = pd.read_sql(
                f"SELECT * FROM `Personal Info` WHERE NRIC={nric}", cnx)
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[1]/div[2]/input").send_keys(data['NRIC'].item())
            sleep(1.3)

            # Name
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[2]/div[1]/input").send_keys(data['Name'].item())
            sleep(1)

            # Gender
            gender = data['Gender'].item()
            if gender == "male" or "Male":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[2]/div[3]/div[2]/p-radiobutton[1]/div/div[2]").click()
            elif gender == "female" or "Female":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[2]/div[3]/div[2]/p-radiobutton[2]/div/div[2]").click()
            sleep(1)

            # Nationality
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[2]/div[4]/p-dropdown/div/span").click()
            if len(nric) == 12:
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[2]/div[4]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[1]/li").click()
            else:
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[2]/div[4]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[2]/li").click()
            sleep(1)

            # Race
            malay = "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[2]/div[5]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[1]/li"
            chinese = "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[2]/div[5]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[2]/li"
            indian = "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[2]/div[5]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[3]/li"
            other = "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[2]/div[5]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[4]/li"

            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[2]/div[5]/p-dropdown/div/span").click()
            race = data['Race'].item()
            if race.capitalize() == "Malay":
                driver.find_element(By.XPATH, malay).click()
            elif race.capitalize() == "Chinese":
                driver.find_element(By.XPATH, chinese).click()
            elif race.capitalize() == "Indian":
                driver.find_element(By.XPATH, indian).click()
            else:
                driver.find_element(By.XPATH, other).click()
            sleep(1)

            # Email Address
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[2]/div[6]/input").send_keys(data['Email'])
            sleep(3)

            # Reg Address
            postal_code_pattern = r"\d{5}(?:(?:-|\s*)\d{4})?"
            regaddress = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div:nth-child(3) > app-customer-information > div > form > div > div:nth-child(3) > div:nth-child(1) > app-address-input > form > div:nth-child(1) > div:nth-child(1) > p-dropdown > div > span').click()"
            driver.execute_script(regaddress)
            address = data['Address'].item()
            postalCode = re.search(postal_code_pattern, address).group()
            print(get_location_by_postcode(postalCode)[0])
            stateSpan = wait.until(EC.visibility_of_element_located(
                (By.XPATH, f"//span[text()=\"{get_location_by_postcode(postalCode)[0]}\"]")))
            stateSpan.click()
            sleep(3)

            # Reg Address 2
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[3]/div[1]/app-address-input/form/div[1]/div[2]/p-dropdown/div/span").click()
            citySpan = wait.until(EC.visibility_of_element_located(
                (By.XPATH, f"//span[text()=\"{get_location_by_postcode(postalCode)[1]}\"]")))
            citySpan.click()
            sleep(3)

            # Reg Address 3
            driver.find_element(
                By.XPATH, "/html/body/app-root/div/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[3]/div[1]/app-address-input/form/div[2]/div[1]/p-dropdown/div").click()
            postcodeSpan = wait.until(EC.visibility_of_element_located(
                (By.XPATH, f"//span[text()=\"{postalCode}\"]")))
            clickPostcodeSpan = ActionChains(driver)
            clickPostcodeSpan.move_to_element(postcodeSpan).click().perform()
            sleep(3)

            address_pattern = r"^(.*),?\s*\d{5}(?:(?:-|\s*)\d{4})?.*$"
            address_line = re.search(address_pattern, address).group(1)
            driver.find_element(
                By.XPATH, '/html/body/app-root/div/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[3]/div[1]/app-address-input/form/div[2]/div[2]/div[1]/input').send_keys(address_line)
            driver.find_element(
                By.XPATH, '/html/body/app-root/div/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[3]/div[2]/app-address-input/form/div[2]/div[2]/div[1]/input').send_keys(address_line)

            # Contact Address
            contactaddress = "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[3]/div[2]/app-address-input/form/div[2]/div[2]/div[1]/div/button"
            driver.find_element(By.XPATH, contactaddress).click()
            sleep(3)

            # Phone No.
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[3]/app-customer-information/div/form/div/div[4]/div[1]/input").send_keys(data['Phone Number'].item())
            sleep(1)

            # Next0
            Next0 = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-d-flex.p-jc-center.button > div:nth-child(2) > a').click()"
            driver.execute_script(Next0)
            sleep(3)

            # Page 2/7 Employment
            # Occupation
            Factory_Operator_list = ['factory worker']
            Clerical_Staff_list = ['manager / assistant manager', 'admin', 'clerk',
                                    'general manager / assistant general manager', 'junior executive',
                                    'Managing director', 'officer / executive',
                                    'senior executive', 'senior executive 2',
                                    'senior general manager', 'supervisor']
            Promotor_Cashier_Shop_assistant_list = [
                'waiter/waitress', 'cabin crew', 'saleman / promoter']
            Own_business_hawker_list = [
                'hawker / taxi driver', 'insurance', 'pensioner / retiree']
            Government_servants_list = ['police / navy / army / post man']
            General_Worker_list = [
                'professional ( lawyer , doctor )', 'teacher / lecturer', 'general worker']

            driver.find_element(
                By.XPATH, "//*[@id='occupation']/div/span").click()
            queryWorkingInfo = f"SELECT * FROM `Working Info` WHERE NRIC = {nric}"
            dfworkingInfo = pd.read_sql(queryWorkingInfo, cnx)

            occupation = dfworkingInfo['Position'].item()
            xpath = "//span[text()='{}']"

            if occupation in General_Worker_list:
                print(xpath.format('General worker'))
                occupationSpan = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, xpath.format('General worker'))))
                occupationSpan.click()

            elif occupation in Factory_Operator_list:
                occupationSpan = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, xpath.format('Factory operator'))))
                occupationSpan.click()

            elif occupation in Clerical_Staff_list:
                occupationSpan = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, xpath.format('Clerical staff'))))
                occupationSpan.click()

            elif occupation in Promotor_Cashier_Shop_assistant_list:
                occupationSpan = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, xpath.format('Promotor/cashier/shop assistant'))))
                occupationSpan.click()

            elif occupation in Own_business_hawker_list:
                occupationSpan = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, xpath.format('Own business-hawker'))))
                occupationSpan.click()

            elif occupation in Government_servants_list:
                occupationSpan = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, xpath.format('Government servant'))))
                occupationSpan.click()

            else:
                occupationSpan = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, xpath.format('Unemployed'))))
                occupationSpan.click()
            sleep(1.5)

            # Employer Name
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[4]/app-employment/div/form/div[2]/div[1]/input").send_keys('testing')
            sleep(1)

            # Monthly Income
            print('Arrived montly income')
            driver.find_element(By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[4]/app-employment/div/form/div[2]/div[2]/div[2]/sigv-input-number/span/input").send_keys(
                dfworkingInfo['Gross Salary'].item()[2::])
            sleep(1)

            # Work Address
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[4]/app-employment/div/form/div[4]/div/div/app-address-input/form/div[2]/div[2]/div[1]/div/button[2]").click()
            sleep(1)

            # Work Phone No.
            driver.find_element(By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[4]/app-employment/div/form/div[5]/div[1]/input").send_keys(
                dfworkingInfo['Company Phone Number'].item())
            sleep(1)

            # Working in Singapore
            if dfworkingInfo['Working in Singapore'].item().lower() == "no":
                pass
            else:
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[4]/app-employment/div/form/div[5]/div[2]/div[2]/div[1]/div/p-radiobutton/div/div[2]").click()
            sleep(1)

            # Next1
            Next1 = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-d-flex.p-jc-center.button > div:nth-child(2) > a').click()"
            driver.execute_script(Next1)
            sleep(3)

            # Page 3/7 Guarantor 1
            # Add

            queryReferenceContact = f"SELECT * FROM `Reference Contact` WHERE NRIC={nric}"
            dfReferenceContact = pd.read_sql(queryReferenceContact, cnx)

            add1 = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div:nth-child(5) > app-guarantor-person > div.step-container.p-fluid.no-border.no-person.ng-star-inserted > div > button').click()"
            add2 = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div:nth-child(5) > app-guarantor-person > div.p-field.mb-button.p-d-flex.p-jc-center.ng-star-inserted > button').click()"
            driver.execute_script(add1)
            sleep(1.3)
            driver.execute_script(add2)
            sleep(1.3)

            # ID No.
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div/div[2]/form/div[1]/div[2]/input").send_keys(dfReferenceContact.iloc[0, 1])
            sleep(1)

            # Name
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div/div[2]/form/div[2]/div[1]/input").send_keys(dfReferenceContact.iloc[0, 2])
            sleep(1)

            # Relationship
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div/div[2]/form/div[2]/div[2]/p-dropdown/div/span").click()
            sleep(1)
            relationship1 = dfReferenceContact.iloc[0, -1]
            if relationship1 == "spouse":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div/div[2]/form/div[2]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[2]/li").click()
            elif relationship1 == "sibling":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div[1]/div[2]/form/div[2]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[9]/li").click()
            elif relationship1 == "parents":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div[1]/div[2]/form/div[2]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[1]/li").click()
            elif relationship1 == "friend":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div[1]/div[2]/form/div[2]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[7]/li").click()
            sleep(1)

            # Mobile Phone No.
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div/div[2]/form/div[3]/div/input").send_keys(dfReferenceContact.iloc[0, 3][2::])
            sleep(1)

            # Guarantor 2
            # ID No.
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div[2]/div[2]/form/div[1]/div[2]/input").send_keys(dfReferenceContact.iloc[0, 1])
            sleep(1)

            # Name
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div[2]/div[2]/form/div[2]/div[1]/input").send_keys(dfReferenceContact.iloc[0, 2])
            sleep(1)

            # Relationship
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div[2]/div[2]/form/div[2]/div[2]/p-dropdown/div/span").click()
            sleep(1)
            relationship2 = dfReferenceContact.iloc[1, -1]
            if relationship2 == "spouse":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div[2]/div[2]/form/div[2]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[2]/li").click()
            elif relationship2 == "sibling":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div[2]/div[2]/form/div[2]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[9]/li").click()
            elif relationship2 == "parents":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div[2]/div[2]/form/div[2]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[1]/li").click()
            elif relationship2 == "friend":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div[2]/div[2]/form/div[2]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[7]/li").click()
            sleep(1)

            # Mobile No.
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[5]/app-guarantor-person/div[1]/div[2]/div[2]/form/div[3]/div/input").send_keys(dfReferenceContact.iloc[1, 3][2::])
            sleep(1)

            # Next2
            Next2 = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-d-flex.p-jc-center.button > div:nth-child(2) > a').click()"
            driver.execute_script(Next2)
            sleep(2)

            # Page 4/7 Contact 1(Emergency)
            # Add
            add3 = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div:nth-child(6) > app-contact-person > div > div > button').click()"
            add4 = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div:nth-child(6) > app-contact-person > div.p-field.mb-button.p-d-flex.p-jc-center.ng-star-inserted > button').click()"
            driver.execute_script(add3)
            sleep(1.3)
            driver.execute_script(add4)
            sleep(1.3)

            # Name
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[1]/form/div[1]/div[1]/input").send_keys(dfReferenceContact.iloc[0, 2])
            sleep(1)

            # Relationship
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[1]/form/div[1]/div[2]/p-dropdown/div/span").click()
            if relationship1 == "spouse":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[1]/form/div[1]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[2]/li").click()
            elif relationship1 == "siblings":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[1]/form/div[1]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[9]/li").click()
            elif relationship1 == "parents":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[1]/form/div[1]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[1]/li").click()
            elif relationship1 == "friend":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[1]/form/div[1]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[7]/li").click()
            sleep(1.2)

            # Mobile Phone No
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[1]/form/div[2]/div/input").send_keys(dfReferenceContact.iloc[0, 3][2::])
            sleep(1)

            # Contact 2(Emergency)
            # Name
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[2]/form/div[1]/div[1]/input").send_keys(dfReferenceContact.iloc[1, 2])
            sleep(1)

            # Relationship
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[2]/form/div[1]/div[2]/p-dropdown/div/span").click()
            if relationship2 == "spouse":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[2]/form/div[1]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[2]/li").click()
            elif relationship2 == "siblings":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[2]/form/div[1]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[9]/li").click()
            elif relationship2 == "parents":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[2]/form/div[1]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[1]/li").click()
            elif relationship2 == "friend":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[2]/form/div[1]/div[2]/p-dropdown/div/div[3]/div/ul/p-dropdownitem[7]/li").click()
            sleep(1.2)

            # Mobile Phone No
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[6]/app-contact-person/div[2]/form/div[2]/div/input").send_keys(dfReferenceContact.iloc[1, 3][2::])
            sleep(1)

            # Next3
            Next3 = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-d-flex.p-jc-center.button > div:nth-child(2) > a').click()"
            driver.execute_script(Next3)
            sleep(2)

            # Page 5/7
            # vehicle_or_motor = "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[7]/app-collateral/div[1]/div/p-accordion/div/p-accordiontab/div/div[1]/a"
            # driver.find_element(By.XPATH,vehicle_or_motor).click()
            # sleep(5)

            # Brand
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[7]/app-collateral/div[1]/div/p-accordion/div/p-accordiontab/div/div[2]/div/div[1]/div[2]/app-collateral-vehicle-motor/div/form/div/div[1]/div[1]/p-dropdown/div/span").click()
            sleep(1)
            brandSpan = wait.until(EC.visibility_of_element_located(
                (By.XPATH, f"//span[text()=\"{dfProductInfo['Brand'].item()}\"]")))
            brandSpan.click()

            sleep(2)

            # Model
            driver.find_element(
                By.XPATH, "/html/body/app-root/div/app-layout/div/div/div/app-process/div[2]/div/div[7]/app-collateral/div[1]/div/p-accordion/div/p-accordiontab/div/div[2]/div/div[1]/div[2]/app-collateral-vehicle-motor/div/form/div/div[1]/div[2]/div[2]/div/p-autocomplete/span/input").send_keys(dfProductInfo['Modal'].item())
            sleep(2)

            # Date of Manufacture
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[7]/app-collateral/div[1]/div/p-accordion/div/p-accordiontab/div/div[2]/div/div[1]/div[2]/app-collateral-vehicle-motor/div/form/div/div[1]/div[3]/div[2]/p-calendar/span/input").send_keys("012023")
            sleep(1.2)

            # Purchase Price
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[7]/app-collateral/div[1]/div/p-accordion/div/p-accordiontab/div/div[2]/div/div[1]/div[2]/app-collateral-vehicle-motor/div/form/div/div[1]/div[7]/div[2]/sigv-currency/div/sigv-input-number/span/input").send_keys('20000')
            sleep(1.2)

            # Down Payment
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[7]/app-collateral/div[1]/div/p-accordion/div/p-accordiontab/div/div[2]/div/div[1]/div[2]/app-collateral-vehicle-motor/div/form/div/div[2]/div/div[2]/sigv-currency/div/sigv-input-number/span/input").send_keys('10000')
            sleep(2.2)

            # Next4
            Next4 = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-d-flex.p-jc-center.button > div:nth-child(2) > a').click()"
            driver.execute_script(Next4)
            sleep(1.5)
            okbutton = "/html/body/p-dynamicdialog/div/div/div/sigv-error-dialog-accordion/div[3]/div/div/button"
            driver.find_element(By.XPATH, okbutton).click()
            sleep(1.5)
            driver.execute_script(Next4)
            sleep(2)

            # Page 6/7
            # Sales
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[8]/app-terms-conditions/div/div[1]/div[2]/div/p-dropdown/div/span").click()
            sleep(1)
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[8]/app-terms-conditions/div/div[1]/div[2]/div/p-dropdown/div/div[3]/div/ul/p-dropdownitem[1]/li").click()
            sleep(1.2)

            # Apply Terms
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[8]/app-terms-conditions/div/div[2]/div[2]/div/p-dropdown/div/span").click()
            tenure = dfProductInfo['Tenure'].item()[:2]
            sleep(1)
            if tenure == "60":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[8]/app-terms-conditions/div/div[2]/div[2]/div/p-dropdown/div/div[3]/div[2]/ul/p-dropdownitem[5]/li").click()
            elif tenure == "48":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[8]/app-terms-conditions/div/div[2]/div[2]/div/p-dropdown/div/div[3]/div[2]/ul/p-dropdownitem[4]/li").click()
            elif tenure == "36":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[8]/app-terms-conditions/div/div[2]/div[2]/div/p-dropdown/div/div[3]/div[2]/ul/p-dropdownitem[3]/li").click()
            elif tenure == "24":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[8]/app-terms-conditions/div/div[2]/div[2]/div/p-dropdown/div/div[3]/div[2]/ul/p-dropdownitem[2]/li").click()
            elif tenure == "12":
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[2]/div/div[8]/app-terms-conditions/div/div[2]/div[2]/div/p-dropdown/div/div[3]/div[2]/ul/p-dropdownitem[1]/li").click()
            sleep(1.2)

            # Next5
            Next5 = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-d-flex.p-jc-center.button > div:nth-child(2) > a').click()"
            driver.execute_script(Next5)
            sleep(3)

            # Page 7/7
            application_Form = r"C:\Users\jerwo\Downloads\contracts.pdf"

            # Download Application Form
            driver.find_element(
                By.XPATH, "/html/body/app-root/div[1]/app-layout/div/div/div/app-process/div[1]/div/div/div[3]/a").click()
            sleep(3)

            # Upload Application Form
            dfPdf = pd.read_sql(f"SELECT pdfFilePath FROM `Banking Info` WHERE NRIC={nric}", cnx)
            PDF_doc = dfPdf['pdfFilePath'].item()
            if PDF_doc.endswith('.pdf'):
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div/app-layout/div/div/div/app-process/div[2]/div/div[9]/app-attachment/div/div/div/p-accordion/div/p-accordiontab[1]/div/div[2]/div/sigv-file-center/div[1]/label/input").send_keys(os.path.abspath(f"../{PDF_doc}"))
                sleep(2)
            else:
                with zipfile.ZipFile(f'../{PDF_doc}', 'r') as zip_ref:
                    for file_name in zip_ref.namelist():
                        if file_name.endswith('.pdf'):
                            zip_ref.extract(file_name)
                driver.find_element(
                    By.XPATH, "/html/body/app-root/div/app-layout/div/div/div/app-process/div[2]/div/div[9]/app-attachment/div/div/div/p-accordion/div/p-accordiontab[1]/div/div[2]/div/sigv-file-center/div[1]/label/input").send_keys(os.path.abspath(f"./{PDF_doc.split('.zip')[0].split('/')[-1]}.pdf"))
                sleep(2)
            sleep(2)
            # Confirm
            driver.find_element(
                By.XPATH, "/html/body/div[2]/div/div[3]/div/button[2]").click()
            sleep(2)

            # Agree Terms to Chailease
            tick_box = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-field-checkbox.mb-5.mt-7.ng-star-inserted > p-checkbox > div > div.p-checkbox-box').click()"
            driver.execute_script(tick_box)
            sleep(2)

            # Submit Button
            submit = "document.querySelector('body > app-root > div.layout-wrapper > app-layout > div > div > div > app-process > div.page-action-container.p-d-flex.mb-20.currency.currency-rwd.ng-star-inserted > div > div > div:nth-child(1) > a').click()"
            driver.execute_script(submit)
    except Exception as e:
        print(e)
        continue
