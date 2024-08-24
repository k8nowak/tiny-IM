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


# Generate What Students Do
prompt_result="""Being as concise as possible, summarize what students do in this lesson in one sentence. 
For example, this might look like: 'in groups of 4, plan a pizza party and estimate the costs'. 
Here are the contents of the lesson:"""+lesson_content

result = make_api_call(prompt_result)

text=str(result.choices[0].message)

what_students_do = extract_message(text)


# Generate What Students Learn
lines = lesson_content.splitlines()
start_extracting = False
goals=[]
for line in lines:
    if "Learning Goals" in line:
        start_extracting = True
    if "Required Preparation" in line:
        start_extracting = False
    if start_extracting:
        goals.append(line)

goal_text='\n'.join(goals)


prompt_what_students_learn="""As concisely as possible, and in plain language, list the 2-3 most 
important math topics, concepts, and skills that students learn in this lesson. Return your answer 
as a numbered list. Your response should be quite short. For example, this might look like: '(1) 
to use expressions, equations, and inequalities to build a mathematical model (2) that a constraint 
limits possible or reasonable values'. Here is a verbose version of the lesson's goals and targets:"""+goal_text

what_students_learn=make_api_call(prompt_what_students_learn)
text=str(what_students_learn.choices[0].message)

what_students_learn = extract_message(text)
what_students_learn = '\n'.join(what_students_learn.split('\n'))



# Generate Where It Fits
prompt_where_it_fits="""Create one very short snippet that describes the purpose this lesson serves 
in the overall unit. You should give me an incomplete sentence with NO fillers like 'This lesson 
serves as...' or 'The purpose of this lesson is...' For example, this might look like: 'a reminder 
of expressions, equations, and inequalities; an introduction to modeling'. Pay special attention 
to the Lesson Narrative. Just give me the incomplete-sentence, highlight snippet of the most 
concise possible explanation, with no filler words.  Here is the content of the lesson:"""+lesson_content

where_it_fits=make_api_call(prompt_where_it_fits)
text=str(where_it_fits.choices[0].message)

where_it_fits = extract_message(text)


# Extract Required Preparation
lines = lesson_content.splitlines()
start_extracting = False
req_prep=[]
for line in lines:
    if line=="Required Preparation":
        start_extracting = True
    if "Standards Alignment" in line:
        start_extracting = False
    if start_extracting:
        req_prep.append(line)

req_prep_text='\n'.join(req_prep)


# Extract Standards
lines = lesson_content.splitlines()
start_extracting = False
standards=[]
for line in lines:
    if line=="Building On":
        start_extracting = True
    if "Glossary" in line:
        start_extracting = False
    if start_extracting:
        standards.append(line)

standards_text='\n'.join(standards)


# Extract Timing
# Splitting the text into lines
lines = lesson_content.splitlines()

# Initializing variables to store the desired lines
total_activity_time = ""
total_lesson_time = ""

# Iterating through the lines to find the relevant information
for line in lines:
    if "Total activity time:" in line:
        total_activity_time = line
    elif "Total lesson time:" in line:
        total_lesson_time = line

# Combining the results
timings = "\n".join([total_activity_time, total_lesson_time])


collected_outputs.append("\n--- Lesson Headers ---\n")
collected_outputs.append(header_text)

collected_outputs.append("\n--- What Students Do ---\n")
collected_outputs.append(what_students_do)

collected_outputs.append("\n--- What Students Learn ---\n")
collected_outputs.append(what_students_learn)

collected_outputs.append("\n--- Where It Fits ---\n")
collected_outputs.append(where_it_fits)

collected_outputs.append("\n--- Required Preparation ---\n")
collected_outputs.append(req_prep_text)

collected_outputs.append("\n--- Standards Alignment ---\n")
collected_outputs.append(standards_text)

collected_outputs.append("\n--- Timing ---\n")
collected_outputs.append(timings)


collected_outputs_text='\n\n'.join(collected_outputs)

# Put it all in a text file
# Assuming lesson_headers contains the required headers in the correct order
unit_number = lesson_headers[0].strip().replace(" ", "_")  # Unit #
unit_name = lesson_headers[1].strip().replace(" ", "_")  # Unit Name
lesson_number = lesson_headers[2].strip().replace(" ", "_")  # Lesson #
lesson_name = lesson_headers[3].strip().replace(" ", "_")  # Lesson Name

# Combine to create a unique filename
filename = f"header_contents/{unit_number}_{unit_name}_{lesson_number}_{lesson_name}.txt"

# Write the collected_outputs_text to this unique filename
with open(filename, 'w') as output_file:
    output_file.write(collected_outputs_text)

print(f"Output saved to {filename}")
