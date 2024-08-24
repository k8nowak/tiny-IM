import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
use_model = 'gpt-4o-mini'

client = OpenAI(api_key=api_key)

def make_api_call(prompt):
    completion = client.chat.completions.create(
        model=use_model,
        messages=[
            {"role": "system", "content": "You are a math curriculum design expert, knowledgeable of the common core state standards and problem-based instruction."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
        )
    return completion

def extract_message(text):
    start_marker_single = "content='"
    start_marker_double = 'content="'
    result = ""

    start_single = text.find(start_marker_single)
    start_double = text.find(start_marker_double)

    if start_single != -1:
        start = start_single + len(start_marker_single)
        end = text.find("'", start)
        if end != -1:
            result = text[start:end]
        else:
            result = None  # Handle the case where the end quote is not found
    elif start_double != -1:
        start = start_double + len(start_marker_double)
        end = text.find('"', start)
        if end != -1:
            result = text[start:end]
        else:
            result = None  # Handle the case where the end quote is not found
    else:
        result = None  # Handle the case where neither start marker is found

    if result:
        result = result.replace("\\n", "\n")  # Replace escaped newlines with actual newlines
        
    return result



# Open the file in read mode
with open('lesson_contents/Function_Notation.txt', 'r') as file:
    # Read the contents of the file
    lesson_content = file.read()


with open('lesson_contents/Function_Notation.txt', 'r') as file:
    # Read the contents of the file
    # lesson_content = file.read()
    lesson_lines = file.readlines()

# List to store all the outputs
collected_outputs = []

# Extract Lesson Headers
lesson_headers=lesson_lines[0:5]
header_text = '\n'.join(lesson_headers)

# Extract Each Activity
sections = {}
current_section = None
section_name = None
section_content = []

for line in lesson_content.splitlines():
    line = line.strip()

    if line.lower() == "warm-up":
        if section_name and section_content:
            sections[section_name] = "\n".join(section_content)
        section_name = "Warm-up"
        section_content = []

    elif line.lower() == "activity":
        if section_name and section_content:
            sections[section_name] = "\n".join(section_content)
        section_name = f"Activity {len(sections) + 1}"
        section_content = []

    else:
        if section_name:
            section_content.append(line)

if section_name and section_content:
    sections[section_name] = "\n".join(section_content)

warm_up = sections.get("Warm-up", "")
activity_1 = sections.get("Activity 1", "")
activity_2 = sections.get("Activity 2", "")

print(warm_up)

# # Generate What Students Do
# prompt_result="""Being as concise as possible, summarize what students do in this lesson in 
# one sentence. For example, this might look like: 
# 'in groups of 4, plan a pizza party and estimate the costs'. 
# Here are the contents of the lesson:"""+lesson_content

# result = make_api_call(prompt_result)

# text=str(result.choices[0].message)

# what_students_do = extract_message(text)





# # Extract Standards
# lines = lesson_content.splitlines()
# start_extracting = False
# standards=[]
# for line in lines:
#     if line=="Building On":
#         start_extracting = True
#     if "Glossary" in line:
#         start_extracting = False
#     if start_extracting:
#         standards.append(line)

# standards_text='\n'.join(standards)





# collected_outputs.append("\n--- Lesson Headers ---\n")
# collected_outputs.append(header_text)




# collected_outputs_text='\n\n'.join(collected_outputs)

# # Put it all in a text file
# # Assuming lesson_headers contains the required headers in the correct order
# unit_number = lesson_headers[0].strip().replace(" ", "_")  # Unit #
# unit_name = lesson_headers[1].strip().replace(" ", "_")  # Unit Name
# lesson_number = lesson_headers[2].strip().replace(" ", "_")  # Lesson #
# lesson_name = lesson_headers[3].strip().replace(" ", "_")  # Lesson Name

# # Combine to create a unique filename
# filename = f"activity_contents/{unit_number}_{unit_name}_{lesson_number}_{lesson_name}_acts.txt"

# # Write the collected_outputs_text to this unique filename
# with open(filename, 'w') as output_file:
#     output_file.write(collected_outputs_text)

# print(f"Output saved to {filename}")