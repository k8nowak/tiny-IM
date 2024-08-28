"""
This script deletes specific lines from text files in the input directory and saves the modified files in the output directory. It removes the lines that match the phrases specified in the 'phrases_to_delete' list. Additionally, it keeps only the first occurrence of lines that match the phrases specified in the 'phrases_to_keep_once' list. The script processes all text files in the input directory and creates corresponding modified files in the output directory.
Parameters:
    input_dir (str): The directory path where the input text files are located.
    output_dir (str): The directory path where the modified text files will be saved.
Returns:
    None: The function saves the modified text files in the output directory.
"""

import os
import glob

unitnum = '6'
process_all_files = True

# Define the input and output directories
input_dir = f'unit-{unitnum}/lesson_contents/'
output_dir = f'unit-{unitnum}/lesson_contents_b/'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Define the list of phrases to delete
phrases_to_delete = [
    '### Activity',
    '#### Student response',
    '### Student Response',
    '## Preparation',
    'Practice', 
    '### Other Resources', 
    'View Student Lesson', 
    '## Teacher Support', 
    '## Student Handouts', 
    '### Instructional Routines',
    '### Materials',
    '#### To Copy (from Blackline Masters)',
    '#### To Gather',
    'CC BY-NC 4.0',
    'Preparation',
    'Lesson',
    'Image description: Course Icon'
]

# Phrases to keep only the first occurrence of
phrases_to_keep_once = [
    '## Standards Alignment',
    '### Building On',
    '### Addressing',
    '### Building Toward'
]

# Phrases to replace
phrases_to_replace = [
    ('Lesson Preamble', '# Lesson Preamble'),
    ('Lesson Content', '# Lesson Content'),
    ('## Warm-up', '## Activity'),
    ('### Student-Facing Goal', '## Student-Facing Goal'),
    ('### Student-Facing Targets', '## Student-Facing Targets'),
    ('### Standards Alignment', '## Standards Alignment'),
    ('#### Building On', '### Building On'),
    ('#### Addressing', '### Addressing'),
    ('#### Building Toward', '### Building Toward')
]

# List of exceptions where '# ' should not be removed
exceptions = [
    '# Lesson Location',
    '# Lesson Preamble',
    '# Lesson Timing',
    '# Lesson Content',
    '# Lesson Close',
]

# List of exceptions where '## ' should not be removed
exceptions2 = [
    '## Unit Number',
    '## Unit Name',
    '## Lesson Number',
    '## Lesson Title',
    '## Total Lesson Time incl Lesson Synthesis',
    '## Total Activity Time in Minutes',
    '## Lesson Narrative',
    '## Learning Goals',
    '## Student-Facing Goal',
    '## Student-Facing Targets',
    '## Required Preparation',
    '## Glossary',
    '## Activity',
    '## Lesson Synthesis',
    '## Student Lesson Summary',
    '## Learning Goals',
]

multi_line_keys = [
    '## Lesson Narrative',
    '### Student Task Statement',
    '### Activity Narrative',
    '### Launch',
    '### Building on Student Thinking',
    '### Are You Ready for More?',
    '## Lesson Synthesis',
    '## Student Lesson Summary',
]

def process_file(input_file, output_dir):
    base_name = os.path.basename(input_file)
    output_file = os.path.join(output_dir, base_name)
    
    seen_phrases = {phrase: False for phrase in phrases_to_keep_once}
    timing_line = ''  # To store the activity timing line

    # Flag to track if we're inside the "Lesson Content" section and to skip lines
    in_lesson_content_section = False

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        previous_line = ''
        flag = 0
        activity_section = False  # To track if we're inside the Activity section
        inside_multiline = False  # To track if we're inside a multi-line section
        
        for line in infile:
            stripped_line = line.strip()

            # Check if the line contains activity timing (e.g., '10 mins')
            if stripped_line.endswith('mins') and stripped_line[0].isdigit():
                timing_line = line
                continue  # Don't write the timing line yet

            # If the line matches a phrase to delete, skip it
            if stripped_line in phrases_to_delete:
                continue

            # Replace phrases as needed
            for phrase, replacement in phrases_to_replace:
                if stripped_line == phrase:
                    line = line.replace(phrase, replacement)
                    stripped_line = stripped_line.replace(phrase, replacement)

            # Start handling the "Lesson Content" section
            if stripped_line == '# Lesson Content':
                in_lesson_content_section = True
                outfile.write(line)
                continue  # Write "Lesson Content" and move on to the next line

            # End of "Lesson Content" section when we reach "## Activity"
            if in_lesson_content_section and stripped_line.startswith('## Activity'):
                in_lesson_content_section = False

            # Skip lines between "# Lesson Content" and "## Activity"
            if in_lesson_content_section:
                continue

            # If '## Activity' is detected, insert timing before the title
            if stripped_line == "## Activity":
                activity_section = True
                outfile.write(line)
                if timing_line:
                    outfile.write(f"### Activity Timing\n{timing_line}")
                    timing_line = ''  # Clear the timing line after writing
                continue  # Skip writing the activity line again

            # Detecting the pattern for activity title insertion
            if activity_section and stripped_line.startswith("### "):
                # Write the activity title without '### '
                line = line.replace('### ', '')
                outfile.write("### Activity Title\n")
                activity_section = False  # Reset the flag after writing the title

            # Detecting the pattern for closing header insertion
            if stripped_line == "## Lesson Synthesis":
                outfile.write("# Lesson Close\n")
            
            # If the line matches a phrase to keep only once
            if stripped_line in phrases_to_keep_once:
                if not seen_phrases[stripped_line]:
                    outfile.write(line)
                    seen_phrases[stripped_line] = True
                continue

            # Remove '# ' if the line is not in the exceptions
            if stripped_line.startswith('# ') and stripped_line not in exceptions:
                line = line.replace('# ', '', 1)
            
            # Remove '## ' if the line is not in the exceptions
            if stripped_line.startswith('## ') and stripped_line not in exceptions2:
                line = line.replace('## ', '', 1)
            
            if flag == 0 and previous_line.strip() == "# Lesson Preamble":
                flag = 1
                continue
            
            # End the multi-line block if a new header is encountered and we are inside a multi-line block
            if inside_multiline and stripped_line.startswith('#'):
                outfile.write(f"\"\"\"\n")
                inside_multiline = False

            # Write the current line to the output file
            outfile.write(line)
            
            # Start a multi-line block if the line is in the multi_line_keys
            if stripped_line in multi_line_keys:
                outfile.write(f"\"\"\"\n")
                inside_multiline = True

            # Save the current line as the previous line for the next iteration
            previous_line = line

        # Ensure that we close any multi-line section if the file ends while still inside one
        if inside_multiline:
            outfile.write(f"\"\"\"\n")

    print(f"Processed {input_file} -> {output_file}")



# Process a single file or all files based on the 'files' variable
if not process_all_files:
    input_file = f'unit-{unitnum}/lesson_contents/algebra-1-Unit-{unitnum}-Lesson-1.txt'
    process_file(input_file, output_dir)
elif process_all_files:
    # Loop through all text files in the input directory
    for input_file in glob.glob(os.path.join(input_dir, '*.txt')):
        process_file(input_file, output_dir)

print("Processing complete. Check the output folder for the results.")
