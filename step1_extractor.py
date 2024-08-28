#!/usr/bin/env python
# coding: utf-8

# Edit the info in lines 12-14 to specify the unit
# This pulls all the lessons in the unit and saves them as text files in the lesson_contents folder
# Then move on to step2. 
# You can alter the bottom of the script to test one lesson rather than a whole unit's worth. 

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

course = 'algebra-1'
unit_num = '6'
unit_name = 'Introduction to Exponential Functions'

# set for processing all the lessons in the unit, or just one
process_all_lessons = False

# if processing one lesson, indicate which one
if not process_all_lessons:
    one_section = 'a'
    one_lesson = 1

lesson_content_template = """
# Lesson Location
## Unit Number
{unit_num}
## Unit Name
{unit_name}
## Lesson Number 
{lesson_num}
## Lesson Title
{lesson_title}
# Lesson Timing
## Total Activity Time in Minutes 
{total_activity_time}
## Total Lesson Time incl Lesson Synthesis
{total_lesson_time} 

{prep_content}

{extracted_content}


"""


def check_url(s,l):
    lesson_url = f'https://accessim.org/9-12-aga/{course}/unit-{unit_num}/section-{s}/lesson-{l}?a=teacher'
    prep_url = f'https://accessim.org/9-12-aga/{course}/unit-{unit_num}/section-{s}/lesson-{l}/preparation?a=teacher'
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


def get_lesson_contents(lesson_url, prep_url):
    # Fetch the webpage content

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


    text2 = ''
    text3 = ''
    for element in soup.body.find_all():
        text = ''
        if element.name in ['h1', 'h2', 'h3','h4','p', 'li']:
            text = element.get_text().strip().replace('\n', '')
            if element.name == 'h1':
                text = f"# {text}"
            elif element.name == 'h2':
                text = f"## {text}"
            elif element.name == 'h3':
                text = f"### {text}"
            elif element.name == 'h4':
                text = f"#### {text}"
        elif element.name == 'img' and element.get('alt') and element['alt'] != 'Expand image':
            text = f"Image description: {element['alt'].strip()}"
        elif element.name == 'div' and 'im-c-icon-heading__title' in element.get('class', []):
            text = element.get_text().strip().replace('\n', '')

        if text and text != text2 and text != text3:
            extracted_content.append(text)
            text3 = text2
            text2 = text

        if element.name == 'table':
            table = element
            table_data = []
            headers = [header.text.replace('\n', '').replace('\t', '').replace('\xa0', ' ') for header in table.find_all('th')]
            table_data.append(headers)
            for row in table.find_all('tr'):
                cells = [cell.text.replace('\n', '').replace('\t', '').replace('\xa0', ' ') for cell in row.find_all('td')]
                if cells:
                    table_data.append(cells)
            for row in table_data:
                extracted_content.append(row)

    # Convert list items to strings before joining
    extracted_content_str = []
    for item in extracted_content:
        if isinstance(item, list):
            extracted_content_str.append(' | '.join(item))  # Convert lists (like tables) to a string
        else:
            extracted_content_str.append(item)

    # Delete boilerplate at beginning
    stop_at = '©2024 Illustrative Mathematics®. Licensed under CC BY-NC 4.0.'
    if stop_at in extracted_content_str:
        stop_index = extracted_content_str.index(stop_at) + 1
        extracted_content_str = extracted_content_str[stop_index:]

    # Extract and sum up all time values
    total_time = 0
    time_pattern = re.compile(r'(\d+)\s*mins')

    for content in extracted_content_str:
        if isinstance(content, str):  # Ensure the content is a string
            match = time_pattern.search(content)
            if match:
                total_time += int(match.group(1))


    # Now get lesson goals from prep page
    response = requests.get(prep_url)
    response.raise_for_status()  # This will raise an exception for HTTP errors

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    prep_content = []
    text = ''
    text2 = ''
    
    for element in soup.body.find_all():
        if element.name in ['h1', 'h2', 'h3', 'h4', 'p', 'li','a']:
            text = element.get_text().strip().replace('\n', '')
            if element.name == 'h1':
                text = f"# {text}"
            elif element.name == 'h2':
                text = f"## {text}"
            elif element.name == 'h3':
                text = f"### {text}"
            elif element.name == 'h4':
                text = f"#### {text}"

        if text and text != text2:
            if text == 'Building On':
                text = 'Standards Alignment' + '\n' + text
            prep_content.append(text)
            text2 = text

    # Delete boilerplate at beginning
    if stop_at in prep_content:
        stop_index = prep_content.index(stop_at) + 1
        prep_content = prep_content[stop_index:]

    prep_content.insert(0, "\n\nLesson Preamble")
    extracted_content_str.insert(0, "\n\nLesson Content")

    # Combine and format the extracted content using the template
    combined_content = lesson_content_template.format(
        unit_num=unit_num,
        unit_name=unit_name,
        lesson_num=lesson_num,
        lesson_title=lesson_title,
        prep_content='\n'.join(prep_content),
        extracted_content='\n'.join(extracted_content_str),
        total_activity_time=total_time,
        total_lesson_time=total_time + 10
    )

    title_string = lesson_title.replace(" ", "_")
    folder = Path(f'unit-{unit_num}/lesson_contents')

    # Combine and save the extracted information
    if folder.is_dir():
        filename = f'unit-{unit_num}/lesson_contents/' + course +'-Unit-'+ unit_num+'-Lesson-'+lesson_num + '.txt'
    else:
        filename = title_string + '.txt'
    with open(filename, 'w') as file:
        file.write(combined_content)
        print(f"Lesson {lesson_num} extracted and saved to {filename}")


if(process_all_lessons):
    section=['a','b','c','d','e','f']
    for s in section:
        for l in range(1,25):
            lesson_url,prep_url=check_url(s,l)
            if(lesson_url!=''):
                print('Processing Lesson: '+str(l))
                get_lesson_contents(lesson_url,prep_url)
else:
    lesson_url,prep_url=check_url(one_section,one_lesson)
    if(lesson_url!=''):
        get_lesson_contents(lesson_url,prep_url)