import re
import json
import os

unitnum = '6'

def parse_text_file(filename):
    with open(filename, 'r') as file:
        content = file.read()

    # First split by main sections
    sections = re.split(r'^\# (.+)$', content, flags=re.MULTILINE)
    lesson_dict = {}

    for i in range(1, len(sections), 2):
        section_title = sections[i].strip()
        section_content = sections[i + 1].strip()
        lesson_dict[section_title] = parse_subsections(section_content)

    return lesson_dict

def parse_subsections(content):
    subsections = re.split(r'^\#\# (.+)$', content, flags=re.MULTILINE)
    sub_dict = {}

    for i in range(1, len(subsections), 2):
        sub_title = subsections[i].strip()
        sub_content = subsections[i + 1].strip()

        if sub_title == "Glossary":
            sub_dict[sub_title] = parse_glossary(sub_content)
        elif sub_title == "Activity":
            sub_dict.setdefault("Activities", []).append(parse_activity(sub_content))
        elif '###' in sub_content:
            sub_dict[sub_title] = parse_nested_subsections(sub_content)
        else:
            sub_dict[sub_title] = clean_content(sub_content)

    return sub_dict

def parse_glossary(content):
    glossary_items = re.split(r'^\#\#\# (.+)$', content, flags=re.MULTILINE)
    glossary_dict = {}

    for i in range(1, len(glossary_items), 2):
        term = glossary_items[i].strip()
        definition = clean_content(glossary_items[i + 1].strip())
        glossary_dict[term] = definition

    return glossary_dict

def parse_activity(content):
    activity_subsections = re.split(r'^\#\#\# (.+)$', content, flags=re.MULTILINE)
    activity_dict = {}

    for i in range(1, len(activity_subsections), 2):
        title = activity_subsections[i].strip()
        sub_content = clean_content(activity_subsections[i + 1].strip())
        activity_dict[title] = sub_content

    return activity_dict

def parse_nested_subsections(content):
    nested_subsections = re.split(r'^\#\#\# (.+)$', content, flags=re.MULTILINE)
    nested_dict = {}

    for i in range(1, len(nested_subsections), 2):
        nested_title = nested_subsections[i].strip()
        nested_content = nested_subsections[i + 1].strip()
        nested_dict[nested_title] = clean_content(nested_content)

    return nested_dict

def clean_content(content):
    # Handle lists, multi-line strings, and any necessary formatting
    if content.startswith('"""') and content.endswith('"""'):
        return content.strip('"""').strip()
    elif '\n' in content:
        return [line.strip() for line in content.split('\n') if line.strip()]
    else:
        return content

def save_to_json(data, output_filename):
    with open(output_filename, 'w') as json_file:
        json.dump(data, json_file, indent=2)

def process_all_files(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop through each file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(input_folder, filename)
            parsed_data = parse_text_file(file_path)
            
            # Create the output file path
            output_filename = filename.replace('.txt', '.json')
            output_path = os.path.join(output_folder, output_filename)
            
            # Save the parsed data to JSON
            save_to_json(parsed_data, output_path)
            print(f"Processed: {filename}")

# Example usage
input_folder = f'unit-{unitnum}/lesson_contents_b2'
output_folder = f'unit-{unitnum}/lesson_contents_c'
process_all_files(input_folder, output_folder)
