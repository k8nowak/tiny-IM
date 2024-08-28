import os


unitnum = '6'

# Toggle between processing one file or all files
process_all_files = True

# Define the input and output directories
input_dir = f'unit-{unitnum}/lesson_contents_b/'
output_dir = f'unit-{unitnum}/lesson_contents_b2/'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

def process_file(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        previous_line = ''
        in_synthesis = False
        in_glossary = False
        first_glossary = True

        for line in infile:
            stripped_line = line.strip()

            if stripped_line == '':
                continue

            if stripped_line == '## Required Preparation':
                outfile.write(line)
                outfile.write(f"\"\"\"\n")
                continue

            if stripped_line == '## Standards Alignment':
                outfile.write(f"\"\"\"\n")
                outfile.write(line)
                continue

            if stripped_line == '### Activity Synthesis':
                outfile.write(line)
                outfile.write(f"\"\"\"\n")
                in_synthesis = True
                continue

            if stripped_line == '## Activity' and in_synthesis:
                outfile.write(f"\"\"\"\n")
                outfile.write(line)
                in_synthesis = False
                continue

            if stripped_line == '# Lesson Close' and in_synthesis:
                outfile.write(f"\"\"\"\n")
                outfile.write(line)
                in_synthesis = False
                continue

            if stripped_line == '## Glossary':
                in_glossary = True

            if stripped_line == '# Lesson Content':
                if previous_line.strip() != '## Glossary':
                    outfile.write(f"\"\"\"\n")
                in_glossary = False

            if in_glossary and stripped_line.startswith('###'):
                if first_glossary:
                    outfile.write(line)
                    outfile.write(f"\"\"\"\n")
                    first_glossary = False
                    continue
                else:
                    outfile.write(f"\"\"\"\n")
                    outfile.write(line)
                    outfile.write(f"\"\"\"\n")
                    continue

            # Write the current line to the output file
            outfile.write(line)

            previous_line = line

    print(f"Processed {input_file} -> {output_file}")




if process_all_files:
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            input_file_path = os.path.join(input_dir, filename)
            output_file_path = os.path.join(output_dir, filename)
            process_file(input_file_path, output_file_path)
else:
    input_file = os.path.join(input_dir, f'algebra-1-Unit-{unitnum}-Lesson-1.txt')
    output_file = os.path.join(output_dir, f'algebra-1-Unit-{unitnum}-Lesson-1.txt')
    process_file(input_file, output_file)
