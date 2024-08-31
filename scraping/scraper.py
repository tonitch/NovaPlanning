from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from datetime import datetime   
import dateparser
import json
import time
import os

from course_info import course_info
from course_math import course_math
from course_physics import course_physics
from course_chimie import course_chimie

course_dict = {"INFO": course_info, "MATH": course_math, "PHYS": course_physics, "CHIMIE": course_chimie}

WAITING_TIME = 5
output = {}

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
    recap = driver.find_element(By.XPATH, '//div[text()="Options"]')
    action = ActionChains(driver)
    action.move_to_element(recap)
    action.move_by_offset(70,30)
    action.click()
    action.perform()


def move_to_combo(driver):
    select = driver.find_element(By.XPATH, '//div[@class="ocb_cont as-input as-select  ie-ripple"]')
    action = ActionChains(driver)
    action.move_to_element(select)
    action.move_by_offset(5,5)
    action.click()
    action.perform()

def move_down(driver,n,begin_enter=False):
    time.sleep(0.2)
    action = ActionChains(driver)
    if(begin_enter):
        action.send_keys(Keys.ENTER)
    for i in range(n):
       action.send_keys(Keys.ARROW_DOWN)
    action.send_keys(Keys.ENTER)
    action.perform()
    WebDriverWait(driver, 10).until(EC.staleness_of)

def get_information(driver,name, course_id):
    if course_id not in output:
        output[course_id] = {}
    output[course_id][name] = {}
    print(name)
    course = course_dict[course_id]
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH,'//table[@class="as-content"]/tbody/tr')))
    time.sleep(0.2)
    tables = driver.find_elements(By.XPATH,'//table[@class="as-content"]/tbody/tr')
    # print(tables)
    color = getColor("")

    for i in range(1,len(tables),2):
        course_name = tables[i].find_elements(By.XPATH,'./td/table/tbody/tr/td/span')[0].text
        print(course_name)
        if course_name in course:
            course_name, color_ = course[course_name]
            color = getColor(color_)
        if course_name not in output[course_id][name]:
            output[course_id][name][course_name] = []
        list_cursus = tables[i+1].find_elements(By.XPATH,'./td/div/table/tbody/tr')
        for cursus in list_cursus:
            info  = cursus.find_elements(By.XPATH,'./td')
            date  = info[0].find_element(By.XPATH,'./div').get_attribute("innerHTML").replace("&nbsp;", " ")
            _time = info[1].get_attribute("innerHTML").replace("&nbsp;", " ")
            row_date = dateparser.parse(date + ' ' + _time[3:8])
            if row_date != None:
                start = row_date.strftime("%Y-%m-%dT%H:%M:%S")
                end   = dateparser.parse(date + ' ' + _time[10:17]).strftime("%Y-%m-%dT%H:%M:%S")

                teacher = info[3].get_attribute("innerHTML").replace("&nbsp;", " ")
                room = info[4].get_attribute("innerHTML").replace("&nbsp;", " ")
                title = course_name + '\n' + teacher + '\n' + room

                output[course_id][name][course_name].append({'title':title,'start':start,'end':end, 'color': color})


options = Options()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)

driver.get("https://hplanning2024.umons.ac.be/invite")
move_to_start_position(driver)
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,11)
get_information(driver,"BAB1 CHIMIE", "CHIMIE")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,5)
get_information(driver,"BAB1 INFO", "INFO")
print(output)
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,1)
get_information(driver,"BAB1 MATH", "MATH")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,2)
get_information(driver,"BAB1 PHYS", "PHYS")

move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,16)
get_information(driver,"BAB2 CHIMIE", "CHIMIE")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,5)
get_information(driver,"BAB2 INFO", "INFO")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,1)
get_information(driver,"BAB2 MATH", "MATH")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,2)
get_information(driver,"BAB2 PHYS", "PHYS")

move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,16)
get_information(driver,"BAB3 CHIMIE", "CHIMIE")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,5)
get_information(driver,"BAB3 INFO", "INFO")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,1)
get_information(driver,"BAB3 MATH", "MATH")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,2)
get_information(driver,"BAB3 PHYS", "PHYS")

move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,44)
get_information(driver,"MASTER CHIMIE", "CHIMIE")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,12)
get_information(driver,"MASTER INFO", "INFO")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,3)
get_information(driver,"MASTER MATH", "MATH")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,1)
get_information(driver,"MASTER MATH DIDA", "MATH")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,4)
get_information(driver,"MASTER PHYS", "PHYS")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,1)
get_information(driver,"MASTER PHYS DIDA", "PHYS")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,82)
get_information(driver,"AESS CHIMIE", "CHIMIE")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,4)
get_information(driver,"AESS MATH", "MATH")
move_to_combo(driver)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'liste-as-options')))
move_down(driver,1)
get_information(driver,"AESS PHYS", "PHYS")

driver.close()

with open('events.json', 'w') as my_file:
    my_file.writelines(json.dumps(output, indent=4))
