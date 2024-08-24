import os
import re

def remove_activity_between_launch_and_student_task(content):
    # This regex will match "Launch" followed by anything, then "Activity" on its own line,
    # but it will stop capturing when it hits "Student Task Statement" by using a negative lookahead.
    pattern = r'(Launch[\s\S]*?)\nActivity\n([\s\S]*?)(?=\nStudent Task Statement)'

    # Replace the match for "Activity" on its own line
    replacement = r'\1\2'

    # Substitute the found patterns in the content
    content = re.sub(pattern, replacement, content)
    
    return content

def process_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    updated_content = remove_activity_between_launch_and_student_task(content)
    
    with open(file_path, 'w') as file:
        file.write(updated_content)

def process_all_files_in_folder(folder_path):
    # Loop through all files in the specified folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):  # Assuming the files are .txt files
            file_path = os.path.join(folder_path, filename)
            process_file(file_path)
            print(f"Processed {filename}")

# Replace 'your_folder_path' with the path to your actual folder
process_all_files_in_folder('lesson_contents_b')
