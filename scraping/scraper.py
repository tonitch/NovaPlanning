from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, MoveTargetOutOfBoundsException

from datetime import datetime   
import dateparser
import json
import time
import os
import random
import re

with open('course.json') as json_file:
    course_dict = json.load(json_file)

with open('year_dict.json') as json_file:
    year_dict = json.load(json_file)

WAITING_TIME = 5
output = {}
list_names = []

colorTab = {
    "BLUE": "#5c98ff",
    "RED": "#fc4747",
    "CYAN": "#44fcdb",
    "ORANGE": "#fca044",
    "GREY": "#878787",
    "GREEN": "#00ad3d",
    "PURPLE": "#79007d",
    "YELLOW" : "GREY"
}

def getColor(color):
    if color in colorTab:
        return colorTab[color]
    else:
        return "#0026ad"

def move_to_start_position(driver):
    # Go into "Formations" tab
    formation = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Formations"]')))
    # formation = driver.find_element(By.XPATH, '//div[text()="Formations"]')
    action = ActionChains(driver)
    action.move_to_element(formation)
    action.click()
    action.perform()

    # Go into "Récapitulatif des cours" tab
    recap = driver.find_elements(By.XPATH , '//li[@data-genre="DIPLOME.RECAPCOURS"]')[1]
    action = ActionChains(driver)
    action.move_to_element(recap)
    action.click()
    action.perform()


def move_to_combo(driver):
    select = driver.find_element(By.XPATH, '//div[@class="ocb_cont as-input as-select  ie-ripple"]')
    action = ActionChains(driver)
    action.move_to_element(select)
    action.click()
    action.perform()


def move_down(driver,n,begin_enter=False):
    time.sleep(0.3)
    action = ActionChains(driver)
    if(begin_enter):
        action.send_keys(Keys.ENTER)
    for i in range(n):
       action.send_keys(Keys.ARROW_DOWN)
    action.send_keys(Keys.ENTER)
    action.perform()
    WebDriverWait(driver, 10).until(EC.staleness_of)


temp_filter = [
    "Sc. informatiques",
    "Sc. chimiques",
    "Sc. physiques",
    "Sc. biomédicales",
    "Sc. pharmaceutiques"
    ]

def get_information(driver):

    cursus_id = driver.find_element(By.XPATH,'//div[@id="GInterface.Instances[1].Instances[1].bouton_Edit"]').text

    # if no course skip this cursus
    if len(driver.find_elements(By.XPATH, '//table[@class="Table"]/tbody/tr/td/br'))>0: return True
    
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH,'//table[@class="as-content"]/tbody/tr')))

    # extract year and cursus 
    res = re.search(r"\.?([\w\d.\s]+)\s(?:-|en|–|‑)\s([a-zA-ZÀ-Ÿ-.'\.\s]+)(?:,\s([^\(\)]+))?(\(\w+\))*", cursus_id) # split year, cursus, specialisation and site
    # res = re.search(r"\.?([\w\d.\s]+)\s(?:-|en|–|‑)\s(.+)", cursus_id) # only year and cursus

    if not res:
        print("invalid cursus :", cursus_id)
        return
    
    if res.group(1) not in year_dict:
        year_dict[res.group(1)] = res.group(1)

    year = year_dict[res.group(1)]
    cursus = res.group(2).strip()
    specialisation = res.group(3)
    site = res.group(4)

    if cursus not in temp_filter: return

    print(f"Cursus : {cursus}\nYear : {year}\nSpecialisation : {specialisation}\nSite : {site}")

    # if cursus doesn't exist then create it
    if(cursus not in course_dict):
        course_dict[cursus] = {
            "name": cursus,
            "courses" : {}
            }
        
    print(cursus, year)
        
    # get readable name of cursus and dict of courses
    cursus_name = course_dict[cursus]["name"]
    courses = course_dict[cursus]["courses"]

    if cursus_name not in output:
        print("cursus not found, creating")
        output[cursus_name] = {}

    if specialisation: year + " " + specialisation
    if site: year = year + " " + site

    print("final section :", year)

    if year not in output[cursus_name]:
        output[cursus_name][year] = {}

    tables = driver.find_elements(By.XPATH,'//table[@class="as-content"]/tbody/tr')
    color = getColor("")


    for i in range(1,len(tables),2):
        course_name = tables[i].find_elements(By.XPATH,'./td/table/tbody/tr/td/span')[0].text

        # ignore "_" course
        if len(course_name) < 2 or course_name in output[cursus_name][year]:
            continue

        print(" -",course_name)

        # if the course is in the list we fetch the data
        # else we create a new entry for modification
        if course_name in courses:
            course_name = courses[course_name]["title"]
            color_ = courses[course_name]["color"]
            color = getColor(color_)
        else:
            course_dict[cursus]["courses"][course_name] = {
                "title" : course_name,
                "color" : random.choice(list(colorTab.keys()))
            }


        if course_name not in output[cursus_name][year]:
            output[cursus_name][year][course_name] = []

        list_courses = tables[i+1].find_elements(By.XPATH,'./td/div/table/tbody/tr')
        for course in list_courses:
            info  = course.find_elements(By.XPATH,'./td')
            date  = info[0].find_element(By.XPATH,'./div').get_attribute("innerHTML").replace("&nbsp;", " ")
            _time = info[1].get_attribute("innerHTML").replace("&nbsp;", " ")
            row_date = dateparser.parse(date + ' ' + _time[3:8])
            if row_date != None:
                start = row_date.strftime("%Y-%m-%dT%H:%M:%S")
                end   = dateparser.parse(date + ' ' + _time[10:17]).strftime("%Y-%m-%dT%H:%M:%S")

                teacher = info[3].get_attribute("innerHTML").replace("&nbsp;", " ")
                room = info[4].get_attribute("innerHTML").replace("&nbsp;", " ")
                title = course_name + '\n' + teacher + '\n' + room

                output[cursus_name][year][course_name].append({'title':title,'start':start,'end':end, 'color': color})


options = Options()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)
url = "https://hplanning2024.umons.ac.be/invite"
driver.get(url)
driver.refresh()
end = True
for i in range(248):

    success = False
    while not success:
        try:
            move_to_start_position(driver)
            move_to_combo(driver)
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
            move_down(driver,i)
            get_information(driver)

            with open('course.json', 'w') as my_file:
                my_file.writelines(json.dumps(course_dict, indent=4, ensure_ascii=False))

            with open('year_dict.json', 'w') as my_file:
                my_file.writelines(json.dumps(year_dict, indent=4, ensure_ascii=False))

            with open('events.json', 'w') as my_file:
                my_file.writelines(json.dumps(output, indent=4, ensure_ascii=False))

            success = True

            print(f"{int(i/248*100)}% [{int(i/248*20) * '#' + int(20 - i/248*20) * ' '}]")

            driver.refresh()
        except Exception as e:
            print("error", e)
            driver.close()
            driver = webdriver.Firefox(options)
            driver.get(url)
            driver.refresh()

    driver.implicitly_wait(1)
    

driver.close()

with open('events.json', 'w') as my_file:
    my_file.writelines(json.dumps(output, indent=4, ensure_ascii=False))