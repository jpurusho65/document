import os
import argparse
import itertools
from openai import OpenAI

# Map of languages to their file extensions
language_extensions = {
    "python": [".py"],
    "javascript": [".js"],
    "typescript": [".tsx"],
    # Add more languages and extensions as needed
}

dirs_to_skip = ['.git', '.github']

def guess_language_based_on_extension(file_path, language_extensions):
    """
    Guess the programming language based on the file extension.

    This function takes a file path and a dictionary mapping languages to their file extensions.
    It returns the language that matches the file extension of the given file path.

    Args:
        file_path (str): The path to the file.
        language_extensions (dict): A dictionary mapping languages to their file extensions.

    Returns:
        str: The guessed language. If no match is found, None is returned.
    """
    # Extract the extension from the file path
    _, ext = os.path.splitext(file_path)

    # Iterate over the language_extensions dictionary
    for language, extensions in language_extensions.items():
        if ext in extensions:
            return language

    # Return None or a default value if no match is found
    return None 


def select_prompt(language):
    """
    Select the appropriate prompt based on the language.

    This function takes a language and returns a prompt that is appropriate for that language.

    Args:
        language (str): The programming language.

    Returns:
        str: The prompt for the given language. If no match is found, None is returned.
    """
    prompts = {
        "python": """
            ### Please generate documentation for the following Python source code
            following the PEP 257 docstring convention. Ensure that the source code
            remains unchanged, and only the comments are added or updated. Do not 
            modify any code logic, structure, or import statements. Ensure that the 
            output does not include markdown code block ticks (```). Do not drop or
            omit any of the original code. The code is as follows::###
            """,
        "javascript": """
            ### Please generate documentation for the following JavaScript/TypeScript source code
            following the JSDoc documentation convention. Ensure that the source code
            remains unchanged, and only the comments are added or updated. Do not 
            modify any code logic, structure, or import statements. Ensure that the 
            output does not include markdown code block ticks (```). Do not drop or
            omit any of the original code. The code is as follows::###
            """,
        "typescript": """
            ### Please generate documentation for the following JavaScript/TypeScript source code
            following the JSDoc documentation convention. Ensure that the source code
            remains unchanged, and only the comments are added or updated. Do not 
            modify any code logic, structure, or import statements. Ensure that the 
            output does not include markdown code block ticks (```). Do not drop or
            omit any of the original code. The code is as follows::###
            """
        # Add more languages and prompts as needed
    }
    return prompts.get(language.lower(), None)

def select_prompt_for_diffs(language, diffs):
    """
    Select the appropriate prompt based on the language.

    This function takes a language and returns a prompt that is appropriate for that language.

    Args:
        language (str): The programming language.
        diffs (str): The git diff output of changes

    Returns:
        str: The prompt for the given language. If no match is found, None is returned.
    """
    prompts = {
        "python": f"""
            Based on the following git diff, integrate the updates into the previously
            provided documentation for the source code in python. Update the documentation 
            only for the parts that have changed according to the git diff, and then provide 
            the complete source code with the integrated documentation.
            The git diff is as follows:
            {diffs}
            The original source code with documentation is:
            """,
        "javascript": f"""
            Based on the following git diff, integrate the updates into the previously
            provided documentation for the source code in Java Script. Update the documentation 
            only for the parts that have changed according to the git diff, and then provide 
            the complete source code with the integrated documentation.
            The git diff is as follows:
            {diffs}
            The original source code with documentation is:
            """,
        "typescript": f"""
            Based on the following git diff, integrate the updates into the previously
            provided documentation for the source code in TypeScript. Update the documentation 
            only for the parts that have changed according to the git diff, and then provide 
            the complete source code with the integrated documentation.
            The git diff is as follows:
            {diffs}
            The original source code with documentation is:
            """,
        # Add more languages and prompts as needed
    }
    return prompts.get(language.lower(), None)

def get_documentation(client, file_path, prompt):
    """
    Generate documentation for a given file using OpenAI GPT-4.

    This function reads the content of the specified file and sends it to OpenAI's GPT-4 model
    to generate inline documentation. The function assumes that the client is an initialized
    and authenticated OpenAI client.

    Args:
        client (OpenAI): The OpenAI client used to send requests to GPT-4.
        file_path (str): The path to the file for which documentation is to be generated.
        prompt (str): Prompt to use for OpenAI query

    Returns:
        str: The generated documentation for the file.
    """
    # Load file content
    with open(file_path, 'r') as file:
        content = file.read()

    if content and prompt:
        # Generate documentation using OpenAI GPT-4
        response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"{prompt}"},
                        {"role": "user", "content": f"{content}"}
                    ],
                    temperature=0,
                    seed=100
            )
        return response.choices[0].message.content


def generate_docs(client, start_path, dirs_to_skip):
    """
    Generate documentation for all files in a directory and its subdirectories.

    This function walks through a directory and its subdirectories, and for each file with a recognized
    extension, it generates documentation using the get_documentation function.

    Args:
        client (OpenAI): The OpenAI client used to send requests to GPT-4.
        start_path (str): The path to the directory where the process should start.
    """
    extensions = list(itertools.chain.from_iterable(language_extensions.values()))
    for subdir, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if d not in dirs_to_skip]
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(subdir, file)
                print(f"Generating document for {filepath}")
                language = guess_language_based_on_extension(filepath, language_extensions)
                prompt = select_prompt(language)
                document = get_documentation(client, filepath, prompt)
                if document:
                    with open(filepath, "w") as file:
                        file.write(document)


def update_docs(client, changed_files, git_diff_file):
    for cf in changed_files:
        language = guess_language_based_on_extension(cf, language_extensions)
        with open(git_diff_file, "r") as gd:
            diffs = gd.readlines()
        prompt = select_prompt_for_diffs(language, diffs)
        print(f"Updating document for {cf}")
        document = get_documentation(client, cf, prompt)
        if document:
            with open(cf, "w") as file:
                file.write(document)

    
# Command line argument parsing
parser = argparse.ArgumentParser(description="Generate Documentation")
parser.add_argument("--openai-key", type=str, default=None, help="OpenAI Key")
parser.add_argument("--start-path", type=str, default=".", help="The start path for processing (default: current directory)")
parser.add_argument("--diffs-file", type=str, default=None, help="File containing the git diff of changes")
parser.add_argument("--changed-files", nargs='*', help="List of changed files")
args = parser.parse_args()

if __name__ == "__main__":
    """
    Main function.

    This function is the entry point of the script. It parses command line arguments and starts the documentation
    generation process. If the OpenAI API key is not set in the environment variables, it can be provided as a command
    line argument.
    """
    start_path = args.start_path
    if not os.environ.get('OPENAI_API_KEY'):
        if args.openai_key:
            os.environ['OPENAI_API_KEY'] = args.openai_key
        else:
            parser.print_help()

    client = OpenAI()
    if args.changed_files and args.diffs_file:
        with open(args.changed_files, 'r') as f:
            content = f.readlines()
        with open(args.diffs_file, 'r') as f:
            diffs = f.readlines()
        print(f"Changed files: {content}")
        print(f"Git diffs: {diffs}")
        #update_docs(client, args.changed_files, args.diffs_file)
    else:
        generate_docs(client, args.start_path, dirs_to_skip)