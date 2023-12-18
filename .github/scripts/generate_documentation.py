import os
import json
from openai import OpenAI

import argparse
from git import Repo

def generate_documentation(client, file_path):
    # Load file content
    with open(file_path, 'r') as file:
        content = file.read()

    prompt = """
    You are a programming assistant designed to generate documentation for program source code.
    Analyze the document step by step. Generate detailed in line documentation for the methods.
    Ensure all method parameters, its type, return type are documented. Also generate class level
    documentation where applicable. Output only the documented code and nothing else.
    """

    # Generate documentation using OpenAI GPT-4
    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": f"{prompt}"},
                            {"role": "user", "content": f"{content}"}
                        ],
                        max_tokens=1024
                        )
    return response.choices[0].message.content

def handle_changed_files(client, changed_files):
    docs = {}
    for file_path in changed_files:
        if os.path.isfile(file_path):
            docs[file_path] = generate_documentation(client, file_path)
    return docs

def git_commit(documentation):
    # Set up Git operations
    repo = Repo('.')
    git = repo.git

    # Create a new branch
    new_branch = "docs-update"
    git.checkout('HEAD', b=new_branch)

    # Commit and push documentation
    for file_path, doc in documentation.items():
        doc_file_path = f"{file_path}"  # Assuming markdown format for docs
        with open(doc_file_path, 'w') as file:
            file.write(doc)

        git.add(doc_file_path)

    git.config('user.email', 'action@github.com')
    git.config('user.name', 'GitHub Action')
    git.commit('-m', 'Update documentation')
    git.push('--set-upstream', 'origin', new_branch)
    

# Command line argument parsing
parser = argparse.ArgumentParser(description="Generate Documentation")
parser.add_argument("--files", nargs='*', help="List of changed files")
args = parser.parse_args()

if __name__ == "__main__":
    client = OpenAI()
    client.api_key=os.environ['OPENAI_API_KEY']
    changed_files = args.files
    documentation = handle_changed_files(client, changed_files)
    git_commit(documentation)
