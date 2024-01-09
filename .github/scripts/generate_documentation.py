import os
from openai import OpenAI
import random
import json
import argparse
from git import Repo, GitCommandError

def generate_documentation(client, file_path):
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

    prompt = """
    Please add or update the Javadoc documentation for the following Java source code.
    Ensure that the source code remains unchanged, and only the comments are added or 
    updated according to Javadoc conventions. Do not modify any code logic, structure,
    or import statements. Ensure that the output does not include markdown code block ticks (```).
    Do not drop or omit any of the original code.
    The Java source code is as follows:
    """

    # Generate documentation using OpenAI GPT-4
    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": f"{prompt}"},
                            {"role": "user", "content": f"{content}"}
                        ]
                )
    return response.choices[0].message.content

def remove_code_block_formatting(original_content):
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

def document_changed_files(client, changed_files):
    """
    Generate documentation for a list of changed files.

    This function takes a list of file paths and generates documentation for each file
    using the `generate_documentation` function. It also removes any Markdown formatting
    from the generated documentation.

    Args:
        client (OpenAI): The OpenAI client used for documentation generation.
        changed_files (list[str]): A list of file paths for which documentation needs to be generated.

    Returns:
        dict: A dictionary with file paths as keys and their corresponding generated documentation as values.
    """
    docs = {}
    for cf in changed_files:
        docs[cf] = generate_documentation(client, cf)
    return docs

def git_commit(documentation):
    """
    Commit generated documentation to a Git repository.

    This function creates a new branch, writes the generated documentation to the respective files,
    and commits these changes to the Git repository. It handles Git operations and commits the changes
    under a unique branch name.

    Args:
        documentation (dict): A dictionary containing file paths and their corresponding documentation.

    Raises:
        GitCommandError: If there is an error in Git operations.
    """
    # Set up Git operations
    repo = Repo('.')
    git = repo.git

    # Create and checkout a unique branch
    unique_id = random.randint(1, 1000)
    new_branch = f"docs-update-{unique_id}"
    try:
        git.checkout(new_branch)
    except GitCommandError:
        git.checkout('HEAD', b=new_branch)

    modified_files = []
    # Write documentation and add to Git
    for file_path, doc in documentation.items():
        doc_file_path = file_path
        with open(doc_file_path, 'w') as file:
            file.write(doc)
        git.add(doc_file_path)
        modified_files.append(doc_file_path)

    # Commit and push changes if any files were modified
    if modified_files:
        git.config('user.email', 'action@github.com')
        git.config('user.name', 'GitHub Action')
        commit_message = f"""
            {new_branch} - Updated Documentation\n\n
            This is an automatic APIOverflow assistant generated documentation
            The following files were modified:
            ${modified_files}
            """
        git.commit('-m', commit_message)

        try:
            git.push('--set-upstream', 'origin', new_branch)
            git.checkout('main')
            git.merge(new_branch)
            git.push('origin', 'main')
        except GitCommandError as e:
            print(f"Error pushing to remote: {e}") 
    else:
        print("No files modified")

def cat_file(changed_files):
    """
    Print the content of a list of files.

    This function takes a list of file paths and prints the content of each file to the console.
    It's a utility function used to display file contents.

    Args:
        changed_files (list[str]): A list of file paths whose contents are to be printed.
    """
    for cf in changed_files:
        with open(cf, "r") as f:
            lines = f.readlines()
        [print(l) for l in lines]

def print_parsed_diff(diff_list):
    """
    Print the parsed information from multiple JSON diff files.

    This function reads multiple JSON files, each containing diff information, and prints the paths of changed files
    for each of these diff files. It's used to display the changed files based on diffs provided in JSON format.

    Args:
        diff_list (list[str]): A list of paths to JSON files, each containing diff information.
    """
    cf_list = []
    for diff_file in diff_list:
        with open(diff_file, 'r') as f:
            doc = json.load(f)
        if doc:
            cf_list.extend([cf["path"] for cf in doc["files"]])
    print(f"Changed files: {cf_list}")

# Command line argument parsing
parser = argparse.ArgumentParser(description="Generate Documentation")
parser.add_argument("--files", nargs='*', help="List of changed files")
parser.add_argument("--show", nargs='*', help="List of changed files")
parser.add_argument("--parse", nargs='*', help="Parse JSON diff")
args = parser.parse_args()

if __name__ == "__main__":
    client = OpenAI()
    client.api_key = os.environ['OPENAI_API_KEY']
    if args.files:
        changed_files = args.files
        documentation = document_changed_files(client, changed_files)
        if documentation:
            git_commit(documentation)
    elif args.show:
        documentation = document_changed_files(client, args.show)
        for _ , doc in documentation.items():
            print(doc)
    elif args.parse:
        print_parsed_diff(args.parse)
    else:
        parser.print_help()
