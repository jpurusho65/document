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

def guess_language_based_on_extension(file_path, language_extensions):
    # Extract the extension from the file path
    _, ext = os.path.splitext(file_path)

    # Iterate over the language_extensions dictionary
    for language, extensions in language_extensions.items():
        if ext in extensions:
            return language

    # Return None or a default value if no match is found
    return None 


def select_prompt(language):
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
        language = guess_language_based_on_extension(file_path, language_extensions)
        prompt = select_prompt(language)

        if prompt:
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


def generate_docs(client, start_path):
    extensions = list(itertools.chain.from_iterable(language_extensions.values()))
    for subdir, _, files in os.walk(start_path):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(subdir, file)
                print(f"Generating document for {filepath} ...")
                document = get_documentation(client, filepath)
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
    if not os.environ.get('OPENAI_API_KEY'):
        if args.openai_key:
            os.environ['OPENAI_API_KEY'] = args.openai_key
        else:
            parser.print_help()

    client = OpenAI()
    generate_docs(client, args.start_path)