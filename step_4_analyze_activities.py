import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import glob

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
use_model = 'gpt-4o'

client = OpenAI(api_key=api_key)

def make_api_call(prompt):
    completion = client.chat.completions.create(
        model=use_model,
        messages=[
            {"role": "system", "content": "You are a math curriculum design expert, knowledgeable of the common core state standards and problem-based instruction. Respond in plain language that is easy to understand."},
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
            result = None
    elif start_double != -1:
        start = start_double + len(start_marker_double)
        end = text.find('"', start)
        if end != -1:
            result = text[start:end]
        else:
            result = None
    else:
        result = None

    if result:
        result = result.replace("\\n", "\n")
        
    return result

# Format the warm-up details into a single string
def format_warm_up(warm_up):
    formatted_string = f"""
Warm-Up Title: {warm_up['activity_title']}
Timing: {warm_up['activity_timing_mins']} minutes

Narrative:
{warm_up['activity_narrative']}

Launch:
{warm_up['launch']}

Student Task Statement:
{warm_up['student_task_statement']}

Activity Synthesis:
{warm_up['activity_synthesis']}
"""
    return formatted_string.strip()

# Format activity details into a single string
def format_activity(activity):
    formatted_string = f"""
Activity Title: {activity['activity_title']}
Timing: {activity['activity_timing_mins']} minutes

Narrative:
{activity['activity_narrative']}

Launch:
{activity['launch']}

Student Task Statement:
{activity['student_task_statement']}

Activity Synthesis:
{activity['activity_synthesis']}
"""
    return formatted_string.strip()

# Define a template for the warm-up and activities
template = """
{title}
Timing: {timing} minutes

Task Statement:
{task_statement}

Takeaway:
{takeaway}

Steps:
{steps}

"""

# Create output directory if it doesn't exist
output_directory = "activity_analysis"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Process each JSON file in the input directory
input_directory = "lesson_contents_c"
json_files = glob.glob(os.path.join(input_directory, "*.json"))

for json_file in json_files:
    with open(json_file, "r") as file:
        json_data = file.read()

    # Load JSON data into a Python dictionary
    data = json.loads(json_data)

    # Dictionary to store takeaway responses
    api_responses = {}

    # Process the warm-up
    formatted_warm_up_string = format_warm_up(data['warm_up'])
    prompt = f"""I'm sending you the details of a classroom activity.
    I want you to give me the most succinct possible statement of the main
    takeaway from this activity. What is the one thing we want to make sure
    students understand, learn, practice, or experience as a result of this activity?
    Pay special attention to the activity synthesis: this is the part of the 
    activity plan that communicates to the teacher the main takeaway.
    Do not use any filler words, just give me the essence. That might look something
    like: 'understand what a constraint is in a model' or 'build fluency applying
    the distributive property'.
    Here is the activity:
    """ + formatted_warm_up_string

    result = make_api_call(prompt)
    text = str(result.choices[0].message)
    activity_takeaway = extract_message(text)
    api_responses["Warm-Up Takeaway"] = activity_takeaway

    # Process the warm-up steps
    prompt = f"""I'm sending you the details of a classroom activity.
    I want you to give me the most succinct possible statement of the steps that
    teacher and students will take to complete this activity. If you had to 
    communicate what happens in this activity to the teacher on a small napkin,
    what would you write? Tell the teacher the most important things they have to
    know. Do not use any filler words, just give me the essence.
    Here is an example of what it might look like, but you should tailor this to
    the details of the activity I'll provide. Some activities are simpler than others.
    You might write anywhere from 3-6 steps. Here's an example: 
    '1. Arrange groups of 4.
    2. After 8 minutes, ask groups to share their answers to questions 1 & 2 with another group.
    3. Then work on question 3, which is the tricky one. If students are stuck, solicit an example from another group.
    4. IMPORTANT: Ask “did anyone calculate costs the same way but wrote a different expression.”
    5. Make sure each group specifies what their letters represent—eg, c represents cost of one cheese pizza.
    6. For groups who finish early, as them to figure the cost per square inch of pizza.'
    Here is the activity:
    """ + formatted_warm_up_string

    result = make_api_call(prompt)
    text = str(result.choices[0].message)
    activity_takeaway = extract_message(text)
    api_responses["Warm-Up Steps"] = activity_takeaway

    # Process each activity
    for i, activity in enumerate(data['activities']):
        formatted_activity_string = format_activity(activity)
        prompt = f"""I'm sending you the details of a classroom activity.
        I want you to give me the most succinct possible statement of the main
        takeaway from this activity. What is the one thing we want to make sure
        students understand, learn, practice, or experience as a result of this activity?
        Pay special attention to the activity synthesis: this is the part of the 
        activity plan that communicates to the teacher the main takeaway.
        Do not use any filler words, just give me the essence. That might look something
        like: 'understand what a constraint is in a model' or 'build fluency applying
        the distributive property'.
        Here is the activity:
        """ + formatted_activity_string
        
        result = make_api_call(prompt)
        text = str(result.choices[0].message)
        activity_takeaway = extract_message(text)
        api_responses[f"Activity {i + 1} Takeaway"] = activity_takeaway
        
        prompt = f"""I'm sending you the details of a classroom activity.
        I want you to give me the most succinct possible statement of the steps that
        teacher and students will take to complete this activity. If you had to 
        communicate what happens in this activity to the teacher on a small napkin,
        what would you write? Tell the teacher the most important things they have to
        know. Do not use any filler words, just give me the essence.
        Some activities are simpler than others. You might write anywhere from 3-6 steps. Here's an example:  
        '1. Arrange groups of 4.
        2. After 8 minutes, ask groups to share their answers to questions 1 & 2 with another group.
        3. Then work on question 3, which is the tricky one. If students are stuck, solicit an example from another group.
        4. IMPORTANT: Ask “did anyone calculate costs the same way but wrote a different expression.”
        5. Make sure each group specifies what their letters represent—eg, c represents cost of one cheese pizza.
        6. For groups who finish early, as them to figure the cost per square inch of pizza.'
        Here is the activity:
        """ + formatted_activity_string

        result = make_api_call(prompt)
        text = str(result.choices[0].message)
        activity_takeaway = extract_message(text)
        api_responses[f"Activity {i + 1} Steps"] = activity_takeaway

    # Combine all responses into a single long string
    all_responses = ""

    # Add the Warm-Up response
    if "Warm-Up Takeaway" in api_responses:
        warm_up = data['warm_up']
        all_responses += template.format(
            title=f"Warm-Up: {warm_up['activity_title']}",
            timing=warm_up['activity_timing_mins'],
            task_statement=warm_up['student_task_statement'],
            takeaway=api_responses["Warm-Up Takeaway"],
            steps=api_responses["Warm-Up Steps"]
        )

    # Add the responses for each activity
    for i in range(1, len(data['activities']) + 1):
        takeaway_key = f"Activity {i} Takeaway"
        steps_key = f"Activity {i} Steps"
        if takeaway_key in api_responses and steps_key in api_responses:
            activity = data['activities'][i-1]
            all_responses += template.format(
                title=f"Activity {i}: {activity['activity_title']}",
                timing=activity['activity_timing_mins'],
                task_statement=activity['student_task_statement'],
                takeaway=api_responses[takeaway_key],
                steps=api_responses[steps_key]
            )

    # Get the file stem and construct the output file path
    file_stem = os.path.splitext(os.path.basename(json_file))[0]
    output_file_path = os.path.join(output_directory, f"{file_stem}.txt")

    # Write the combined responses to the output file
    with open(output_file_path, "w") as file:
        file.write(all_responses)

    print(f"Takeaways for {file_stem} have been written to {output_file_path}.")
