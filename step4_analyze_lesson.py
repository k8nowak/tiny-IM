import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
use_model = 'gpt-4o-mini'
unit = 6
lesson_numbers_to_process = [1,2,3]  # Add the lesson numbers you want to process


client = OpenAI(api_key=api_key)

def process_single_lesson(lesson_number):
    filename = f'unit-{unit}/lesson_contents_c/algebra-1-Unit-{unit}-Lesson-{lesson_number}.json'
    output_filename = f'unit-{unit}/lesson_contents_d/gpt_content_lesson_{lesson_number}.md'

    # Load the JSON file
    with open(filename, 'r') as file:
        lesson_data = json.load(file)


    # Entire lesson data dumped into string
    lesson_data_str = json.dumps(lesson_data, indent=4)

    horz_line = "\n\n" + "-"*40 + "\n\n"

    system_prompt = "You are a skilled copy editor focused on making text as concise and clear as possible. Your goal is to rewrite educational content in the simplest, most direct terms. Prioritize brevity, combining ideas when possible, and eliminate any unnecessary words or phrases. Aim for a tone that is straightforward and easy to understand."

    def extract_message(text):
        start_marker_single = "content='"
        start_marker_double = 'content="'
        result = ""

        start_single = text.find(start_marker_single)
        start_double = text.find(start_marker_double)

        if start_single != -1:
            start = start_single + len(start_marker_single)
            
            end = text.find(", role='assistant'", start)
            if end != -1:
                result = text[start:end]
            else:
                result = None  # Handle the case where the end quote is not found
        elif start_double != -1:
            start = start_double + len(start_marker_double)
            
            end = text.find(", role='assistant'", start)
            if end != -1:
                result = text[start:end]
            else:
                result = None  # Handle the case where the end quote is not found
        else:
            result = None  # Handle the case where neither start marker is found

        if result:
            result = result.replace("\\n\n", "\n\n")  # Replace escaped newlines with actual newlines
        
        if result.endswith("'") or result.endswith('"'):
            cleaned = result[:-1]
        else:
            cleaned = result
        
        return cleaned

    def make_api_call(prompt):
        completion = client.chat.completions.create(
            model=use_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
            )
        text=str(completion.choices[0].message)
        result = extract_message(text)
        return result

    def shorten_response(text,prompt_shorten):
        completion = client.chat.completions.create(
            model=use_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_shorten+horz_line+text}
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


    # Function to format dictionaries into a readable string
    def format_dict(input_dict):
        formatted = []
        for key, value in input_dict.items():
            if isinstance(value, list):
                # If the value is a list, join its elements with commas
                formatted.append(f"{key}: {', '.join(value)}")
            else:
                # Otherwise, just append the key-value pair
                formatted.append(f"{key}: {value}")
        return "\n\n".join(formatted)

    # Function to write content to a file with Markdown formatting
    def write_to_file(filename, content, mode='a'):
        with open(filename, mode) as f:
            f.write(content + "\n\n" + horz_line)


    # Function to make responses easier to read in Markdown
    def format_for_markdown(text):
            return text.replace('\\n', '<br>')

    # Extract the standards alignment dictionary
    standards_alignment_dict = get_lesson_data(lesson_data, "Lesson Preamble", "Standards Alignment")

    # Convert it to a readable string
    standards_alignment = "Standards:\n\n" + format_dict(standards_alignment_dict)

    # Extract the glossary dictionary
    glossary_dict = get_lesson_data(lesson_data, "Lesson Preamble", "Glossary")
    if bool(glossary_dict):
        glossary = "Glossary:\n\n" + format_dict(glossary_dict)
    else:
        glossary = "Glossary: \n\nNone."
    

    # Assign lesson components to variables
    unit_number = "Unit Number: "+get_lesson_data(lesson_data, "Lesson Location", "Unit Number")
    unit_title = "Unit Title: "+get_lesson_data(lesson_data, "Lesson Location", "Unit Name")
    lesson_number = "Lesson Number: "+get_lesson_data(lesson_data, "Lesson Location", "Lesson Number")
    lesson_title = "Lesson Title: "+get_lesson_data(lesson_data, "Lesson Location", "Lesson Title")
    lesson_total_time = "Total Time: "+get_lesson_data(lesson_data, "Lesson Location", "Total Lesson Time incl Lesson Synthesis")
    lesson_narrative = "Lesson Narrative: "+get_lesson_data(lesson_data, "Lesson Preamble", "Lesson Narrative")
    learning_goals = "Learning Goals (teacher audience):\n\n" + "\n\n".join(get_lesson_data(lesson_data, "Lesson Preamble", "Learning Goals"))
    learning_targets = "Learning Targets (student audience):\n\n"+"\n\n".join(get_lesson_data(lesson_data, "Lesson Preamble", "Student-Facing Targets"))
    required_preparation = "Required Prep: "+get_lesson_data(lesson_data, "Lesson Preamble", "Required Preparation")
    lesson_synthesis = "Lesson Synthesis (teacher audience): "+get_lesson_data(lesson_data, "Lesson Close", "Lesson Synthesis")
    student_lesson_summary = "Lesson Summary (student audience): "+get_lesson_data(lesson_data, "Lesson Close", "Student Lesson Summary")

    #############################################
    # Extracting activities
    # Activities are stored in three ways:
    # 1. As a long text string in all_activities
    # 2. As a list in activities_list, where activities_list[i] corresponds to the ith activity
    # 3. As a list in activity_essences_list, where which only has narrative, launch, and task statement
    #############################################

    activities = lesson_data.get("Lesson Content", {}).get("Activities", [])
    all_activities = "Activities:\n\n"
    activities_list = []
    activity_essences_list = []

    for i, activity in enumerate(activities):
        # Extract all relevant data from the current activity
        activity_timing = f"Activity {i} Timing: "+activity.get("Activity Timing", "")
        activity_title = activity.get("Activity Title", "")
        activity_narrative = f"Activity {i} Narrative: "+activity.get("Activity Narrative", "")
        launch = f"Activity {i} Launch: "+activity.get("Launch", "")
        student_task_statement = f"Activity {i} Task Statement: "+activity.get("Student Task Statement", "")
        activity_synthesis = f"Activity {i} Synthesis: "+activity.get("Activity Synthesis", "")
        
        # Combine the information into a single string
        activity_info = (
            f"Activity {i} Title: " + activity_title + "\n\n" +
            activity_timing + "\n\n" +
            activity_narrative + "\n\n" +
            launch + "\n\n" +
            student_task_statement + "\n\n" +
            activity_synthesis
        )
        
        activity_essence = (
            activity_narrative + "\n\n" +
            launch + "\n\n" +
            student_task_statement
        )
        
        # Concatenate each piece of activity info into all_activities
        all_activities += activity_info + horz_line
        
        activities_list.append({"content": activity_info, "title": activity_title})  # Store both content and title
        
        all_activity_essences = activity_essence + horz_line
        
        activity_essences_list.append(activity_essence)
        



    # Construct header content
    header_content = "\n\n ".join([
        "# GPT-generated content to start from", 
        unit_title.strip(), 
        lesson_number.strip(), 
        lesson_title.strip()
    ])

    # Start by writing the first section to the file
    write_to_file(output_filename, header_content, mode='w')  # Markdown header

    def create_summary_content():
        prompt_wsd="""In one sentence, describe what students actually do and experience in this lesson, focusing on the most important actions and feelings. Make it brief, natural, and almost conversational, like explaining it to a colleague in a quick chat. Here are the contents of the lesson:"""
        prompt_shorten="""Make this summary as short and straightforward as possible. Imagine you’re describing it in a single breath to a friend, focusing only on the essential actions and student experiences."""

        write_to_file(output_filename, "## What Students Do\n\n")


        what_students_do = make_api_call(prompt_wsd + all_activities)
        write_to_file(output_filename, "### option 1\n\n")
        what_students_do = shorten_response(what_students_do,prompt_shorten)
        write_to_file(output_filename,what_students_do)


        what_students_do = make_api_call(prompt_wsd + lesson_narrative + all_activities)
        write_to_file(output_filename, "### option 2\n\n")
        what_students_do = shorten_response(what_students_do,prompt_shorten)
        write_to_file(output_filename, what_students_do)

        
        # Prompt for rewriting learning goals
        prompt_wsl = """Reduce these learning goals to just the essential keywords and concepts. Remove any unnecessary words. Format as a numbered list using (1), (2), etc."""
        prompt_shorten="""Turn these key concepts into the shortest possible learning goals. Make each statement as brief and direct as possible. Combine similar ideas. Format as a numbered list using (1), (2), etc. Respond with only the shortened goals with no additional labels or commentary."""


        # Adding the section for what students learn
        write_to_file(output_filename, "## What Students Learn\n\n")

        # Generate and write learning goals
        what_students_learn = make_api_call(prompt_wsl + learning_goals)

        # Shorten the response and write it
        what_students_learn = shorten_response(what_students_learn,prompt_shorten)
        write_to_file(output_filename, "### option 1\n\n")
        wsl=format_for_markdown(what_students_learn)
        write_to_file(output_filename, wsl)

        # Generate and write learning goals
        what_students_learn = make_api_call(prompt_wsl + learning_targets)

        # Shorten the response and write it
        what_students_learn = shorten_response(what_students_learn,prompt_shorten)
        write_to_file(output_filename, "### option 2\n\n")
        wsl=format_for_markdown(what_students_learn)
        write_to_file(output_filename, wsl)

        # Prompt for describing where the lesson fits
        prompt_wif = """Describe where this lesson fits in the larger, multi-day instructional unit using the fewest words possible. Use plain, everyday language, and keep it super brief. Your response should be a short phrase or sentence fragment. In rare cases, you can include more than one if the lesson has more than one clear purpose within the unit."""
        prompt_shorten="""Make this summary as short and minimal as possible. Focus only on the most essential purpose of the lesson, in just a few words."""


        # Adding the section for where it fits
        write_to_file(output_filename, "## Where It Fits\n\n")

        # Generate and write where it fits
        where_it_fits = make_api_call(prompt_wif + lesson_narrative)

        # Shorten the response and write it
        where_it_fits = shorten_response(where_it_fits,prompt_shorten)
        write_to_file(output_filename, where_it_fits)

    # Uncomment this to generate the summary content
    create_summary_content()


    # Prompts for Activity Processing
    prompt_getgist = """Summarize the main thing students just learned or realized in this activity. 
    Keep it brief and use simple, clear language, focusing on the key insight or challenge they encountered. 
    Here is the content of the activity:"""

    prompt_shorten = """Cut this summary down to its core message. It should be short, direct, and feel like 
    a summary for a friend about what they just learned. This will be the contents of a slide deck students will see after they complete
    a classroom activity, so the first sentence should be an imperative statement--instead of 'In this activity, you 
    learned that xyz,' just say 'xyz'. Make sure it's easy to understand for a 13-15 year-old audience. """

    prompt_decide = """Play the role of an expert instructional coach. When novice teachers modify an activity from the school's 
    adopted curriculum, they tend to modify it poorly by reducing the thinking students have to do. Teachers should not be afraid 
    to teach grade-level concepts and academic terms, but they should keep the plan straightforward. You are 
    going to help them decide if an activity needs to be modified. It is important to know that we will not be able to make edits
    to any images included in the activity. I'm going to show you a lesson plan for an Algebra 1 classroom 
    activity. I want you to decide if the activity is too complicated for a novice teacher to conduct. The reasons an activity might
    be too complicated include: the plan is excessively complex to execute, or the plan
    includes steps or questions that are unnecessary for achieving the goal of the activity. If it is not too complicated, 
    respond with 'This is not too complicated.' If it is too complicated, say 'This is too complicated.' If you are on the fence, say 
    'This is not too complicated.' Then, provide a brief rationale for your response. Here is the lesson plan for the activity:"""

    prompt_simplify = """Play the role of an experienced instructional coach. I'm going to show you the lesson plan for an Algebra 1 
    activity that is too complicated for a novice teacher to conduct. Make a common-sense, realistic proposal for how to simplify it. 
    If you reuse an image from the original activity, please repeat the 'Image description' in the position where you reuse the image. 
    There are a number of strategies you could use to reduce complexity---be creative here. Your proposal should include a brief description 
    of the changes, and then four sections with the exact headers 'Revised Activity Narrative', 'Revised Launch', 'Revised Student Task Statement', 
    and 'Revised Activity Synthesis'. Be specific in your revised sections, including sample language that a teacher could use 
    and specific actions the teacher should take. You can re-use images from the original activity, repeating the 'Image description' in 
    the position where you reuse the image, but you can't modify any images. Here is the original lesson plan for the activity:"""

    def make_prompt(activity, proposal):
        return f"""Here is a lesson plan for an Algebra 1 classroom activity, followed by a proposal for
        how to simplify it. The proposal includes a brief description of the changes, and then revisions to three sections
        of the plan. The revised sections are 'Revised Activity Narrative', 'Revised Launch', 'Revised Student Task Statement', and 'Revised Activity Synthesis'.
        I want you to respond with a complete, revised activity with the same sections and in the same format as the original lesson plan, 
        but with the proposed changes implemented. Only respond with the complete, revised plan with no additional commentary. 
        Here is the original lesson plan:"""+activity+"""Here is the proposal for simplifying the activity:"""+proposal

    prompt_getsteps = """I'm going to give you a lesson plan for a classroom activity. I need you to encapsulate the
    critical steps for the teacher to take for executing the launch and the student task statement successfully. Do not include
    the activity synthesis in your steps. Do not repeat elements of the student task statement in your steps. Assume the student
    task statement is being displayed on a projector while the activity is being conducted. If there are any super key points 
    the teacher should emphasize or common misunderstandings they should watch out for, include them. Use specifics 
    from the activity, not vague generalities. Be concise and use imperative statements. Integrate your response into one list organized by how events happen in the 
    activity consecutively. Do not use any headers. Here is the teacher's lesson plan for the activity:"""

    prompt_shorten = """I'm going to show you the plan for a classroom activity and a list of steps for executing the launch
    and the student task statement. Simplify the list of steps to the most essential 3-6 actions for conducting the classroom 
    activity successfully, removing any redundant or unnecessary steps. Just reply with the revised steps, with no additional commentary."""

        
        
    write_to_file(output_filename, "# Activity Slides\n\n")

    responses = {}

    # First loop to gather all the necessary responses and decisions
    for i, activity_data in enumerate(activities_list, start=0):  # Start from 0
        
        activity = activity_data["content"]
        activity_title = activity_data["title"]
        
        print(f"Processing Activity {i}")
        # Gist and shortened version
        complicated = False
        gist = make_api_call(prompt_getgist + activity)
        shortened_gist = shorten_response(gist, prompt_shorten)
        
        # Decision on complexity
        decision = make_api_call(prompt_decide + activity)
        
        if "This is not too complicated" in decision:
            activity_content = activity  # Original activity
        elif "This is too complicated" in decision:
            proposal = make_api_call(prompt_simplify + activity)
            prompt = make_prompt(activity, proposal)
            activity_content = make_api_call(prompt)  # Simplified activity
            complicated = True
        else:
            activity_content = activity  # Default to original activity if unclear
        
        # Uncut steps and abbreviated steps
        steps = make_api_call(prompt_getsteps + activity_content)
        shorter_steps = make_api_call(prompt_shorten + " Here is the activity plan: " + activity_content + " Here is the first draft of steps: " + steps)
        
        # Store everything in the responses dictionary
        responses[f"Activity {i}"] = {
            "takeaways": gist,
            "shorter_takeaways": shortened_gist,
            "content": activity_content,
            "complicated": complicated,
            "uncut_steps": steps,
            "abbreviated_steps": shorter_steps,
            "title": activity_title
        }

    # Second loop to write everything to the file in the correct order
    for i, (activity, response) in enumerate(responses.items()):
        write_to_file(output_filename, f"## Activity {i}: {response['title']}\n\n") 
        write_to_file(output_filename, f"### Activity {i} Takeaways\n\n")
        write_to_file(output_filename, response['takeaways'])
        
        write_to_file(output_filename, f"### Activity {i} Contents\n\n")
        if response['complicated']:
            write_to_file(output_filename, f"Activity {i} was too complicated; this is a simplified activity.")
        else:
            write_to_file(output_filename, f"Activity {i} is not too complicated; this is the original.")
        formatted_content = format_for_markdown(response['content'])
        write_to_file(output_filename, formatted_content)
        
        write_to_file(output_filename, f"### Activity {i} Uncut Steps\n\n")
        formatted_uncut_steps = format_for_markdown(response['uncut_steps'])
        write_to_file(output_filename, formatted_uncut_steps)
        
        write_to_file(output_filename, f"### Activity {i} Abbreviated Steps\n\n")
        formatted_abbreviated_steps = format_for_markdown(response['abbreviated_steps'])
        write_to_file(output_filename, formatted_abbreviated_steps)
    
    # return output_filename
        

def process_multiple_lessons(lesson_numbers):
    for lesson_number in lesson_numbers:
        print(f"Processing Lesson {lesson_number}")
        process_single_lesson(lesson_number)

# Usage

process_multiple_lessons(lesson_numbers_to_process)          
        