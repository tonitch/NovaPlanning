from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, MoveTargetOutOfBoundsException, NoSuchElementException

from datetime import datetime
import dateparser
import json
import time
import os
import random
import re

output = {}

temp_filter = [
    "Sc. informatiques",
    "Sc. mathématiques",
    "Sc. chimiques",
    "Sc. physiques",
    "Sc. biomédicales",
    "Sc. pharmaceutiques"
    ]

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

def get_information(driver):

    cursus_id = driver.find_element(By.XPATH,'//div[@id="GInterface.Instances[1].Instances[1].bouton_Edit"]').text

    # if no course skip this cursus
    # if len(driver.find_elements(By.XPATH, '//table[@class="Table"]/tbody/tr/td/br'))>0: return True


    # extract year and cursus 
    res = re.search(r"\.?([\w\d.\s]+)\s(?:-|en|–|‑)\s([a-zA-ZÀ-Ÿ-.'\.\s]+)(?:,\s([^\(\)]+))?(\(\w+\))*", cursus_id) # split year, cursus, specialisation and site
    # res = re.search(r"\.?([\w\d.\s]+)\s(?:-|en|–|‑)\s(.+)", cursus_id) # only year and cursus

    if not res:
        print("invalid cursus :", cursus_id)
        return

    year = res.group(1)
    cursus = res.group(2).strip()
    specialisation = res.group(3)
    site = res.group(4)

    if cursus not in temp_filter:
        print(f"skipping {cursus}")
        return

    print(f"Cursus : {cursus} -- Year : {year} -- Specialisation : {specialisation} -- Site : {site}")

    if cursus not in output:
        output[cursus] = {}
    if year not in output[cursus]:
        output[cursus][year] = {}

    deploy_all_courses(driver)
    get_printable(driver)

    table = driver.find_elements(By.XPATH,'//div[@class="Fenetre_Impression FondBlanc"]//table[@class="FondBlanc Table"]//table[@class="Table"]/tbody/tr')
    color = getColor("")

    list_horaire = []
    for ligne in table:
        # print(ligne.text)
        if "séance" in ligne.text:
            course_name = ligne.find_element(By.XPATH, './td[2]')
            if course_name.text not in output[cursus][year]:
                output[cursus][year][course_name.text] = []
        else:
            left = ligne.find_element(By.XPATH, './td[1]')
            spliter = re.search(r'(.*) de (\d+h\d+) à (\d+h\d+)', left.text)
            date = spliter.group(1) if spliter else left.text
            start = spliter.group(2) if spliter and len(spliter.groups()) >= 2 else ""
            end = spliter.group(3) if spliter and len(spliter.groups()) >= 3 else ""

            right = ligne.find_element(By.XPATH, './td[2]')
            spliter = re.search(r'(.*)(?: - (.*))', right.text)
            room = spliter.group(1) if spliter else right.text
            teacher = spliter.group(2) if spliter else ""

            if start and end:
                start = dateparser.parse(date + ' ' + start).strftime("%Y-%m-%dT%H:%M:%S")
                end = dateparser.parse(date + ' ' + end).strftime("%Y-%m-%dT%H:%M:%S")

                title = course_name.text + '\n' + teacher + '\n' + room
                output[cursus][year][course_name.text].append(
                        {'title':title,'start':start,'end':end, 'color': color}
                        )
    close_printable(driver)

def select_recap_cours(driver):
    formation = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Formations"]')))
    action = ActionChains(driver)
    action.move_to_element(formation)
    action.click()
    action.perform()

    recap = driver.find_elements(By.XPATH , '//li[@data-genre="DIPLOME.RECAPCOURS"]')[1]
    action = ActionChains(driver)
    action.move_to_element(recap)
    action.click()
    action.perform()


def click_dropdown_cours(driver):
    select = driver.find_element(By.XPATH, '//div[@class="ocb_cont as-input as-select  ie-ripple"]')
    action = ActionChains(driver)
    action.move_to_element(select)
    action.click()
    action.perform()
    # WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'liste-as-options')))


def move_down(driver,n, i):
    el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="GInterface.Instances[1].Instances[1]_{i}"]')))
    action = ActionChains(driver)
    for i in range(n):
       action.send_keys(Keys.ARROW_DOWN)
    action.send_keys(Keys.ENTER)
    action.perform()
    WebDriverWait(driver, 10).until(EC.invisibility_of_element(el))


def deploy_all_courses(driver):

    action = ActionChains(driver)
    for i in range(5):
        try:
            first = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.liste_contenu_ligne')))
            action.send_keys_to_element(first, Keys.END)
            action.send_keys(Keys.TAB)
            action.send_keys(Keys.ENTER)
            action.perform()
        except StaleElementReferenceException:
            continue
        finally:
            break

    action = ActionChains(driver)
    while len(driver.find_elements(By.CSS_SELECTOR, '.btn-deploiement.icon_fleche_num')) > 0:
        action.send_keys(Keys.UP)
        action.send_keys(Keys.TAB)
        action.send_keys(Keys.ENTER)
        action.perform()

def get_printable(driver):
    print_icon = driver.find_element(By.CLASS_NAME, 'icon_print')
    action = ActionChains(driver)
    action.move_to_element(print_icon)
    action.click()
    action.perform()

def close_printable(driver):
    close_icon = driver.find_element(By.CLASS_NAME, 'icon_fermeture_widget')
    action = ActionChains(driver)
    action.move_to_element(close_icon)
    action.click()
    action.perform()


options = Options()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)
driver.set_window_size(1920, 1080)
url = "https://hplanning2025.umons.ac.be/invite"
driver.get(url)
driver.refresh()

select_recap_cours(driver)

click_dropdown_cours(driver)
move_down(driver,0, 2)
get_information(driver)

i = 0
while i <=262:
    try:
        click_dropdown_cours(driver)
        move_down(driver,1, i + 2)
        get_information(driver)
        i += 1
        print(f"{i}/262")
    except TimeoutException:
        print("timeout, trying to rescue")
        driver.close()
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        driver.refresh()
        select_recap_cours(driver)
        click_dropdown_cours(driver)
        move_down(driver, i, 2)

driver.close()

with open('events.json', 'w') as my_file:
    my_file.writelines(json.dumps(output, indent=4, ensure_ascii=False))
