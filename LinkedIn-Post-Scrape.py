#!/usr/bin/env python
# coding: utf-8

# In[185]:


#import all the required headers
from selenium import webdriver
import time
import csv
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


# In[186]:


#Get the Credentials from details.txt file for log in
username = ''
password = ''
chrome_driver = ''
link = '' 
with open('details.txt','r') as file:
    lines = file.readlines()
    username = lines[0].split()[2].strip()
    password = lines[1].split()[2].strip()
    chrome_driver = lines[2].split()[2].strip()
    scrape_link = lines[3].split()[2].strip()
file.close()


# In[187]:


#Use the chrome driver to launch chrome and visit linkedin.com
wd = webdriver.Chrome(chrome_driver)
wd.get("https://www.linkedin.com")


# In[188]:


#Enter the credentials and login
time.sleep(1)
wd.find_element_by_xpath('/html/body/nav/section[2]/form/div[1]/div[1]/input').send_keys(username)
time.sleep(1)
wd.find_element_by_xpath('/html/body/nav/section[2]/form/div[1]/div[2]/input').send_keys(password)
time.sleep(1)
wd.find_element_by_xpath('/html/body/nav/section[2]/form/div[2]/button').click()
time.sleep(1)
wd.get(scrape_link)
time.sleep(1)


# In[189]:


#Recursively use the function to get comments from linkedin
def get_comments():
    try:
        wd.find_element_by_xpath("//button[contains(@class,'button comments-comments-list__show-previous-button t-12 t-black t-normal hoverable-link-text')]")
    except NoSuchElementException:
        return False
    return True


# In[ ]:


#Find the element provided by parameter
def check_element(element):
    try:
        wd.find_element_by_xpath(element)
    except NoSuchElementException:
        return False
    return True


link_list = set()

#Create a csv file with headers
csv_columns = ['Name','Location','Linkedin Link','Company','University','Experience']
csv_file ="Result.csv"
try:
    with open(csv_file, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
except IOError:
        print("I/O error")

#Flow for web scraping
while get_comments():
    comments = wd.find_elements_by_xpath("//a[contains(@class,'comments-post-meta__profile-link t-16 t-black t-bold tap-target ember-view')]")
    for comment in comments:
        link = comment.get_attribute('href')
        if not (link in link_list):
            link_list.add(link)
            current_tab = wd.current_window_handle
            script = 'window.open("{}");'.format(link)
            wd.execute_script(script)
            new_tab = [tab for tab in wd.window_handles if tab != current_tab][0]
            wd.switch_to.window(new_tab)
            time.sleep(3)
            name = wd.find_element_by_xpath("//li[contains(@class,'inline t-24 t-black t-normal break-words')]").text
            location = wd.find_element_by_xpath("//li[contains(@class,'t-16 t-black t-normal inline-block')]").text
            exp = wd.find_elements_by_xpath("//span[contains(@class,'text-align-left ml2 t-14 t-black t-bold full-width lt-line-clamp lt-line-clamp--multi-line ember-view')]")
            if len(exp) == 1:
                if(exp[0].text.find('University') >= 0 or exp[0].text.find('Institute') or exp[0].text.find('College') >= 0):
                    university = exp[0].text
                    company = 'N/A'
                else:
                    university = 'N/A'
                    company = exp[0].text
            else:
                company = exp[0].text
                university = exp[1].text
            if company == university:
                company = 'N/A'
            exp_element = '//*[@id="experience-section"]/ul'
            SCROLL_PAUSE_TIME = 1
            last_height = wd.execute_script("return document.body.scrollHeight")
            flag = 0
            while not check_element(exp_element):
                html = wd.find_element_by_tag_name('html')
                html.send_keys(Keys.PAGE_DOWN)
                time.sleep(SCROLL_PAUSE_TIME)
                new_height = wd.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    flag = 1
                    break
                last_height = new_height
            if flag == 0:
                exp_elements = wd.find_element_by_xpath('//*[@id="experience-section"]/ul')
                exp_elements = exp_elements.find_elements_by_tag_name('li')
                experiences = []
                flag = 0
                for exp in exp_elements:
                    for i in range(4):
                        exp = exp.find_elements_by_xpath(".//*")[0]
                        if i == 3 and exp.get_attribute('class') == 'pv-entity__company-details':
                            flag = 1
                            break
                    if flag == 1:
                        break
                    exp = exp.find_elements_by_xpath(".//*")[3]
                    experiences.append(exp.text)
                if flag == 1:
                    exp_elements = wd.find_element_by_xpath("//ul[contains(@class,'pv-entity__position-group mt2')]")
                    exp_elements = exp_elements.find_elements_by_tag_name('li')
                    for exp in exp_elements:
                        experiences.append(exp.find_elements_by_xpath(".//*")[9].text)
                
#                  print(name,location,link,company,university,experiences)
                appl = {"Name":name, "Location":location, "Linkedin Link":link, "Company":company, "University":university,"Experience":experiences}
                
                # Writing to csv file
                try:
                    with open(csv_file, 'a') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                        writer.writerow(appl)
                except IOError:
                    print("I/O error")
            wd.close()
            wd.switch_to_window(current_tab)

    wd.find_element_by_xpath("//button[contains(@class,'button comments-comments-list__show-previous-button t-12 t-black t-normal hoverable-link-text')]").click()


# In[ ]:




