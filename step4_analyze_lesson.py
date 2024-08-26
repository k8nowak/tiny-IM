import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
use_model = 'gpt-4o-mini'

client = OpenAI(api_key=api_key)

filename = 'lesson_contents_c/algebra-1-Unit-5-Lesson-1.json'
# Load the JSON file
with open(filename, 'r') as file:
    lesson_data = json.load(file)

# Entire lesson data dumped into string
lesson_data_str = json.dumps(lesson_data, indent=4)

horz_line = "\n" + "-"*40 + "\n"

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

def make_api_call(prompt):
    completion = client.chat.completions.create(
        model=use_model,
        messages=[
            {"role": "system", "content": "You are a math curriculum design expert, knowledgeable of the common core state standards and problem-based instruction."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
        )
    text=str(completion.choices[0].message)
    result = extract_message(text)
    return result

def shorten_response(text):
    completion = client.chat.completions.create(
        model=use_model,
        messages=[
            {"role": "system", "content": "You are a copy editor who knows how to convey meaning in pithy, plain language."},
            {"role": "user", "content": """Rewrite this copy. Use plain everyday language and make it absolutely 
             as concise as possible while retaining critical meaning. Ruthlessly delete words that aren't absolutely 
             necessary. Any sentence or component should be maximum ten words. If and only if the input is an ordered list, 
             use the same formatting of the list in your output.\n"""+text}
        ],
        max_tokens=1000
        )
    text=str(completion.choices[0].message)
    result = extract_message(text)
    return result


def get_lesson_data(lesson_data, *keys):
    current_data = lesson_data
    for key in keys:
        current_data = current_data.get(key, {})
        if not isinstance(current_data, dict):
            break
    return current_data if current_data else ""


# Function to format the standards dictionary into a readable string
def format_dict(dict):
    formatted = []
    for key, value in dict.items():
        if isinstance(value, list):
            # If the value is a list, join its elements with commas
            formatted.append(f"{key}: {', '.join(value)}")
        else:
            # Otherwise, just append the key-value pair
            formatted.append(f"{key}: {value}")
    return "\n".join(formatted)

# Extract the standards alignment dictionary
standards_alignment_dict = get_lesson_data(lesson_data, "Lesson Preamble", "Standards Alignment")

# Convert it to a readable string
standards_alignment = "Standards:\n" + format_dict(standards_alignment_dict)

# Extract the glossary dictionary
glossary_dict = get_lesson_data(lesson_data, "Lesson Preamble", "Glossary")
glossary = "Glossary:\n" + format_dict(glossary_dict)

# Assign lesson components to variables
unit_number = "Unit Number: "+get_lesson_data(lesson_data, "Lesson Location", "Unit Number")
unit_title = "Unit Title: "+get_lesson_data(lesson_data, "Lesson Location", "Unit Name")
lesson_number = "Lesson Number: "+get_lesson_data(lesson_data, "Lesson Location", "Lesson Number")
lesson_title = "Lesson Title: "+get_lesson_data(lesson_data, "Lesson Location", "Lesson Title")
lesson_total_time = "Total Time: "+get_lesson_data(lesson_data, "Lesson Location", "Total Lesson Time incl Lesson Synthesis")
lesson_narrative = "Lesson Narrative: "+get_lesson_data(lesson_data, "Lesson Preamble", "Lesson Narrative")
learning_goals = "Learning Goals (teacher audience):\n" + "\n".join(get_lesson_data(lesson_data, "Lesson Preamble", "Learning Goals"))
learning_targets = "Learning Targets (student audience):\n"+"\n".join(get_lesson_data(lesson_data, "Lesson Preamble", "Student-Facing Targets"))
required_preparation = "Required Prep: "+get_lesson_data(lesson_data, "Lesson Preamble", "Required Preparation")
lesson_synthesis = "Lesson Synthesis (teacher audience): "+get_lesson_data(lesson_data, "Lesson Close", "Lesson Synthesis")
student_lesson_summary = "Lesson Summary (student audience): "+get_lesson_data(lesson_data, "Lesson Close", "Student Lesson Summary")



# Extracting activities
activities = lesson_data.get("Lesson Content", {}).get("Activities", [])

# Loop through each activity and process it
# Because of this, you can refer to all_activities or activities_list[i] to access the i'th activity

all_activities = "Activities:\n"
activities_list = []

for i, activity in enumerate(activities):
    # print(f"Processing Activity {i+1}:")

    # Extract all relevant data from the current activity
    activity_timing = f"Activity {i} Timing: "+activity.get("Activity Timing", "")
    activity_title = f"Activity {i} Title: "+activity.get("Activity Title", "")
    activity_narrative = f"Activity {i} Narrative: "+activity.get("Activity Narrative", "")
    launch = f"Activity {i} Launch: "+activity.get("Launch", "")
    student_task_statement = f"Activity {i} Task Statement: "+activity.get("Student Task Statement", "")
    activity_synthesis = f"Activity {i} Synthesis: "+activity.get("Activity Synthesis", "")
    
    # Combine the information into a single string
    activity_info = (
        activity_timing + "\n" +
        activity_title + "\n" +
        activity_narrative + "\n" +
        launch + "\n" +
        student_task_statement + "\n" +
        activity_synthesis
    )
    
    # Concatenate each piece of activity info into all_activities
    all_activities += activity_info + horz_line
    
    activities_list.append(activity_info)
    



# prompt_wsd="""Being as concise as possible, summarize what students do in this lesson in one sentence.
# Only include the really key essential stuff that is the core of the lesson. Do not include any nice-to-knows
# or side quests. Really encapsulate it into a super brief description. Eliminate any redundant or unnecessary words. 
# For example, this might look like: 'in groups of 4, plan a pizza party and estimate the costs'. 
# Here are the contents of the lesson: \n"""

# what_students_do = make_api_call(prompt_wsd+lesson_data_str)
# what_students_do = shorten_response(what_students_do)
# print("whole lesson version\n"+what_students_do+horz_line)


# what_students_do = make_api_call(prompt_wsd+all_activities)
# what_students_do = shorten_response(what_students_do)
# print("all activities version\n"+what_students_do+horz_line)


# what_students_do = make_api_call(prompt_wsd+lesson_narrative+lesson_synthesis)
# what_students_do = shorten_response(what_students_do)
# print("narrative+synthesis version\n"+what_students_do+horz_line)


# prompt_wsl="""Being as concise as possible, rewrite these learning goals in plain, everyday language.
# Keep it super pithy: Do not use verbs like "Recognize that..." or "Understand that...", or "Learn how to..." just start the 
# goal with "that" or "to". You can combine two goals into one if they are similar. Format your response 
# as a numbered list using the formatting (1), (2), etc.\n"""
# what_students_learn = make_api_call(prompt_wsl+learning_goals)
# print("Learning Goals version\n\n"+"What students learn\n"+what_students_learn+horz_line)

# what_students_learn = shorten_response(what_students_learn)
# print("Shortened version\n"+what_students_learn+horz_line)

# what_students_learn = make_api_call(prompt_wsl+learning_targets)
# print("Learning Targets version\n\n"+"What students learn\n"+what_students_learn+horz_line)

# what_students_learn = shorten_response(what_students_learn)
# print("Shortened version\n"+what_students_learn+horz_line)


prompt_wif="""Being as concise as possible, describe where this lesson fits in the larger, multi-day 
instructional unit. Use plain, everyday language. Your response should be a sentence fragment with no
subject. For example, your response might look like: 'as a reminder
of expressions, equations, and inequalities; as an introduction to modeling.'\n"""
where_it_fits = make_api_call(prompt_wif+lesson_narrative)
print("Lesson Narrative version\n\n"+"Where It Fits\n"+where_it_fits+horz_line)

where_it_fits = shorten_response(where_it_fits)
print("Shortened version\n"+where_it_fits+horz_line)



