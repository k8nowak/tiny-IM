import re

def remove_activity_between_launch_and_student_task(content):
    # This regular expression finds "Activity" between "Launch" and "Student Task Statement"
    pattern = r'(Launch[\s\S]*?)Activity([\s\S]*?Student Task Statement)'
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

# Replace 'your_file.txt' with the path to your actual file
process_file('lesson_contents_b/Interpreting_and_Creating_Graphs.txt')

