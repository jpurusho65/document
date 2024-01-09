import os
import subprocess
import argparse
import openai
from guesslang import Guess


# Map of languages to their file extensions
language_extensions = {
    "python": [".py"],
    "javascript": [".js"],
    "typescript": [".tsx"],
    # Add more languages and extensions as needed
}

def guess_language(code):
    guess = Guess()
    return guess.language_name(code)


def select_prompt(language, source_code):
    prompts = {
        "Python": f"""
            ### Please generate documentation for the following Python source code
            following the PEP 257 docstring convention. Ensure that the source code
            remains unchanged, and only the comments are added or updated. Do not 
            modify any code logic, structure, or import statements. Ensure that the 
            output does not include markdown code block ticks (```). Do not drop or
            omit any of the original code. The code is as follows::\n{source_code}\n###
            """,
        "JavaScript": f"""
            ### Please generate documentation for the following JavaScript/TypeScript source code
            following the JSDoc documentation convention. Ensure that the source code
            remains unchanged, and only the comments are added or updated. Do not 
            modify any code logic, structure, or import statements. Ensure that the 
            output does not include markdown code block ticks (```). Do not drop or
            omit any of the original code. The code is as follows::\n{source_code}\n###
            """
        # Add more languages and prompts as needed
    }
    return prompts.get(language, None)


def get_documentation(client, file_path):
    """
    Generate documentation for a given file using OpenAI GPT-4.

    This function reads the content of the specified file and sends it to OpenAI's GPT-4 model
    to generate inline documentation. The function assumes that the client is an initialized
    and authenticated OpenAI client.

    Args:
        client (OpenAI): The OpenAI client used to send requests to GPT-4.
        file_path (str): The path to the file for which documentation is to be generated.

    Returns:
        str: The generated documentation for the file.
    """
    # Load file content
    with open(file_path, 'r') as file:
        content = file.read()

    if content:
        language = guess_language(content)
        prompt = select_prompt(language, content)

        if prompt:
            response = client.Completion.create(
                model="gpt-4",
                prompt=prompt,
                temperature=0,
                max_tokens=150  # Adjust as needed
            )
            return response.choices[0].text.strip()


def remove_markdown_code_block_formatting(original_content):
    """
    Remove Markdown code block formatting from a string.

    This function is used to clean up the content that is formatted as a Markdown code block.
    It removes the starting and ending ``` that are used to denote code blocks in Markdown.

    Args:
        original_content (str): The content string with Markdown code block formatting.

    Returns:
        str: The cleaned content without Markdown code block formatting.
    """
    # Split the content into lines
    lines = original_content.split('\n')

    # Remove Markdown code block delimiters
    if lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines[-1].strip() == "```":
        lines = lines[:-1]

    # Join the lines back into a single string
    cleaned_content = '\n'.join(lines)

    return cleaned_content


def generate_docs(client, start_path):
    for subdir, dirs, files in os.walk(start_path):
        for file in files:
            if any(file.endswith(ext) for ext in language_extensions):
                filepath = os.path.join(subdir, file)
                document = client.get_documentation(client, filepath)
                if document:
                    with open(filepath, "w") as file:
                        file.write(document)


# Command line argument parsing
parser = argparse.ArgumentParser(description="Generate Documentation")
parser.add_argument("--openai-key", type=str, help="OpenAI Key")
parser.add_argument("--start-path", type=str, default=".", help="The start path for processing (default: current directory)")
args = parser.parse_args()

if __name__ == "__main__":
    start_path = args.start_path
    if args.openai_key:
        openai.api_key = args.openai_key
        print(f"OpenAI Key: {args.openai_key}")
        print(f"Start Path: {args.start_path}")
        #generate_docs(openai, args.start_path)
    else:
        parser.print_help()