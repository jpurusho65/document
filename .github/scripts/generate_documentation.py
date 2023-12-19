import os
from openai import OpenAI
import random

import argparse
from git import Repo, GitCommandError

def generate_documentation(client, file_path):
    # Load file content
    with open(file_path, 'r') as file:
        content = file.read()

    prompt = """
    You are a programming assistant designed to generate documentation for program source code.
    Analyze the document step by step. Generate detailed in line documentation for the methods.
    Ensure all method parameters, their types, and return types are documented. Also generate class-level
    documentation where applicable. The output must only include the documented code and no other text. 
    Do not add any warnings, usage notes, additional note or comments that are not part of the original
    code's functionality.  The final output must be syntactically correct functional code.
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
    # Split the content into lines
    lines = original_content.split('\n')

    # Check if the first line starts with ```
    if lines[0].strip().startswith("```"):
        # Remove the first line (```language)
        lines = lines[1:]

    # Check if the last line ends with ```
    if lines[-1].strip() == "```":
        # Remove the last line (```)
        lines = lines[:-1]

    # Join the lines back into a single string
    cleaned_content = '\n'.join(lines)

    return cleaned_content


def document_changed_files(client, changed_files):
    docs = {}
    for file_path in changed_files:
        if os.path.isfile(file_path):
            docs[file_path] = remove_code_block_formatting(generate_documentation(client, file_path))
        else:
            print(f"Cannot find file {file_path}")
    return docs


def git_commit(documentation):
    # Set up Git operations
    repo = Repo('.')
    git = repo.git

    # Generate a unique branch name
    unique_id = random.randint(1, 1000)
    new_branch = f"docs-update-{unique_id}"

    # Check if the branch already exists
    try:
        git.checkout(new_branch)
    except GitCommandError:
        # If the branch does not exist, create and checkout the branch
        git.checkout('HEAD', b=new_branch)

    modified_files = []
    # Commit and push documentation
    for file_path, doc in documentation.items():
        doc_file_path = file_path  # Assuming markdown format for docs
        with open(doc_file_path, 'w') as file:
            file.write(doc)

        git.add(doc_file_path)
        modified_files.append(doc_file_path)

    if modified_files:
        # Configure user details for commit
        git.config('user.email', 'action@github.com')
        git.config('user.name', 'GitHub Action')

        # Commit message
        commit_message = f"""
            {new_branch} - Updated Documentation\n\n
            This is an automatic APIOverflow assistent generated documentation
            The following files were modified:
            ${modified_files}
            """

        git.commit('-m', commit_message)

        try:
            git.push('--set-upstream', 'origin', new_branch)
        except GitCommandError as e:
            print(f"Error pushing to remote: {e}") 
    else:
        print("No files modified")
        

def cat_file(changed_files):
    for cf in changed_files:
        lines = []
        with open(cf, "r") as f:
            lines= f.readlines()
        [print(l) for l in lines]


# Command line argument parsing
parser = argparse.ArgumentParser(description="Generate Documentation")
parser.add_argument("--files", nargs='*', help="List of changed files")
args = parser.parse_args()

if __name__ == "__main__":
    client = OpenAI()
    client.api_key=os.environ['OPENAI_API_KEY']
    # if args.files:
    #     changed_files = args.files
    #     documentation = document_changed_files(client, changed_files)
    #     if documentation:
    #         git_commit(documentation)
    # else:
    #     parser.print_help()
    if args.files:
        cat_file(args.files)
