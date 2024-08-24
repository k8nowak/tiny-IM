#!/usr/bin/env python
# coding: utf-8

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

def check_url(s,l):
    lesson_url = f'https://accessim.org/9-12-aga/algebra-1/unit-5/section-{s}/lesson-{l}?a=teacher'
    prep_url = f'https://accessim.org/9-12-aga/algebra-1/unit-5/section-{s}/lesson-{l}/preparation?a=teacher'
    try:
        # Send a GET request to the URL
        response = requests.get(lesson_url)

        # Check if the status code is 200
        if response.status_code == 200:
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Check for common error keywords in the text
            error_keyword = "404 | Lesson"
            keyword_found = False
            for element in soup.body.find_all():
                text = ''
                if element.name in ['p']:  
                    text = element.get_text().strip().replace('\n','')
                    if error_keyword in text:
                        keyword_found = True
                        break
            
            if not keyword_found:
                return(lesson_url,prep_url)  
            elif keyword_found:
                return('','')    
            
        else:
            print(f"URL returned a status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        # Handle exceptions (e.g., network issues, invalid URL)
        print(f"An error occurred: {e}")


def get_lesson_contents(lesson_url,prep_url):
    # Fetch the webpage content
    unit_num='5'
    unit_name='Functions'
    lesson_num = lesson_url.split('/')[-1].split('-')[1].split('?')[0]

    # Get contents of lesson page
    response = requests.get(lesson_url)
    response.raise_for_status()  # This will raise an exception for HTTP errors

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get Lesson Title
    title_list = soup.find_all(class_='im-c-page-heading__title')

    lesson_title = title_list[0].get_text()


    # Interleave text and image alt texts
    extracted_content = []

    to_omit= ['Practice','Preparation','Lesson','Log in to access Student Response.','Student Response','Building on Student Thinking','Are You Ready for More?','Standards Alignment','Instructional Routines','Materials','View Student Lesson']

    text2 = ''
    text3 = ''
    for element in soup.body.find_all():
        text = ''
        if element.name in ['h1','h2','h3','p','li']:
            text = element.get_text().strip().replace('\n','')
        elif element.name == 'img' and element.get('alt') and element['alt'] != 'Expand image':
            text = f"Image description: {element['alt'].strip()}"
        elif element.name == 'div' and 'im-c-icon-heading__title' in element.get('class', []):
            text = element.get_text().strip().replace('\n', '')
                
        if text != '' and text not in to_omit and text != text2 and text != text3:
            extracted_content.append(text)
            text3 = text2
            text2 = text
        
        if element.name == 'table':
            table = element
            table_data = []
            headers = [header.text.replace('\n', '').replace('\t', '').replace('\xa0', ' ') for header in table.find_all('th')]
            table_data.append(headers)
            for row in table.find_all('tr'):
                # Extract each cell from the row
                cells = row.find_all('td')
                # Extract text from each cell and add it to the row_data list
                row_data = [cell.text.replace('\n', '').replace('\t', '').replace('\xa0', ' ') for cell in cells]
                if row_data:
                    table_data.append(row_data)
            for row in table_data:
                extracted_content.append(row)



    # Delete boilerplate at beginning
    stop_at = '©2024 Illustrative Mathematics®. Licensed under CC BY-NC 4.0.'
    if stop_at in extracted_content:
        stop_index = extracted_content.index(stop_at)+1
        extracted_content = extracted_content[stop_index:]

    # Extract and sum up all time values
    total_time = 0
    time_pattern = re.compile(r'(\d+)\s*mins')

    for content in extracted_content:
        if isinstance(content, str):  # Ensure the content is a string
            match = time_pattern.search(content)
            if match:
                total_time += int(match.group(1))

    # print(f"Total time: {total_time} mins")
    extracted_content.insert(0,f"Total lesson time: {total_time+5}–{total_time+10} mins")
    extracted_content.insert(0,f"Total activity time: {total_time} mins")


    # Now get lesson goals from prep page
    response = requests.get(prep_url)
    response.raise_for_status()  # This will raise an exception for HTTP errors

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')


            
    prep_content = []
    text = ''
    text2 = ''
    to_omit=to_omit+['Other Resources','Teacher Support','Student Handouts']
    for element in soup.body.find_all():
        if element.name in ['h1','h2','h3','h4','p','li','a']:
            text = element.get_text().strip().replace('\n','')        
        # elif element.name == 'div' and 'im-c-standards__title' in element.get('class', []):
        #      text = element.get_text().strip().replace('\n', '')
        
        if text != '' and text not in to_omit and text != text2:
            if text == 'Building On':
                text = 'Standards Alignment' + '\n' + text
            prep_content.append(text)
            text2 = text


        

    # Delete boilerplate at beginning
    stop_at = '©2024 Illustrative Mathematics®. Licensed under CC BY-NC 4.0.'
    if stop_at in prep_content:
        stop_index = prep_content.index(stop_at)+1
        prep_content = prep_content[stop_index:]

    prep_content.insert(0,"Unit "+unit_num+"\n"+unit_name+"\nLesson "+lesson_num+"\n"+lesson_title+"\n\nLesson Pramble\n")
    extracted_content.insert(0,"\n\nLesson Content\n")




    combined_content = prep_content+extracted_content


    title_string = lesson_title.replace(" ", "_")
    folder = Path('lesson_contents')

    # Combine and save the extracted information
    if folder.is_dir():
        filename='lesson_contents/'+title_string+'.txt'
    else: filename=title_string+'.txt'
    with open(filename, 'w') as file:
        for item in combined_content:
            file.write(f"{item}\n")


section=['a','b','c','d','e','f']
for s in section:
    for l in range(1,20):
        lesson_url,prep_url=check_url(s,l)
        if(lesson_url!=''):
            get_lesson_contents(lesson_url,prep_url)