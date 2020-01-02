import requests
import re
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from random import randint


def get_domains():
    domains = []
    r = requests.get("https://email-verify.my-addr.com/list-of-most-popular-email-domains.php")
    soup = BeautifulSoup(r.content, 'html5lib')
    domain_content = soup.find('div', attrs={'class': 'content'}).findNext('table')
    for domain in domain_content('tr'):
        domains.append(domain.contents[2].get_text())
    return domains


def get_people():
    people = []
    r = requests.get("https://www.biographyonline.net/people/famous-100.html")
    soup = BeautifulSoup(r.content, 'html5lib')
    article = soup.find('main', attrs={'id': 'content-primary'})
    for person in article.select('ol li'):
        name = re.sub(r'([a-z A-Z.]*)\W.*', r'\1', person.get_text())
        people.append(re.sub(r' $', '', name))
    return people


def getperson(browser, name):
    person = {}
    #    try:
    browser.find_element_by_id('searchInput').send_keys(name)
    browser.find_element_by_id('searchform').submit()
    delay = 3  # seconds
    try:
        WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'firstHeading')))
        if "Search" not in browser.title:
            soup = BeautifulSoup(browser.page_source, 'html5lib')
            if not soup.select('table.infobox.vcard'): return person
            vcard = soup.select('table.infobox.vcard')[0]
            if vcard.select('div', class_="fn"): person['NAME'] = vcard.find('div', class_="fn").get_text()
            if vcard.select('img'): person['IMG_PATH'] = 'https:' + vcard.select('img')[0]['src']
            # card.find_next('span', class_='bday')
            if vcard.find(text='Born'):
                if vcard.find('span', class_='bday'):
                    person['DATE_OF_BIRTH'] = datetime.datetime.strptime(vcard.find('span', class_='bday').get_text(),
                                                                         '%Y-%m-%d')
                    person['PLACE_OF_BIRTH'] = re.match(r'.*\d{4,4}(.*)',
                                                        vcard.find(text='Born').parent.parent.get_text()).group(1)
                else:
                    born_text = vcard.find(text='Born').parent.parent.get_text()
                    match_obj = re.match(r'.*(\d{2,2} \w+ \d{4,4})(.*)', born_text)
                    if match_obj:
                        person['DATE_OF_BIRTH'] = datetime.datetime.strptime(match_obj.group(1), '%B %d, %Y')
                        person['PLACE_OF_BIRTH'] = match_obj.group(2)
            if vcard.find(text='Died'): person['DATE_OF_DEATH'] = datetime.datetime.strptime(
                vcard.find(text='Died').parent.find_next('span', {'style': 'display:none'}).get_text()[1:-1],
                '%Y-%m-%d')
            person['PLACE_OF_BIRTH'] = re.sub(r'^ \(age.*\)', '', person['PLACE_OF_BIRTH'])
        else:
            print('not found')
    except:
        print(name + ': unsuccessful scrape')
        return {}
    return person


people = get_people()  # ['Abraham Lincoln', 'Marilyn Monroe']
domains = get_domains()
print(people)
driver = webdriver.Chrome(
    '/usr/lib/chromium-browser/chromedriver')  # Optional argument, if not specified will search path.
driver.get("https://en.wikipedia.org/wiki/Wiki")

biography = []
for p in people:
    person = getperson(driver, p)
    person['email'] = re.sub(' ', '.', p).lower() + '@' + domains[randint(0, len(domains) - 1)]
    biography.append(person)
    print(person)
