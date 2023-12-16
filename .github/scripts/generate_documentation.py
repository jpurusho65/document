import os
import openai
import argparse
from git import Repo

def generate_documentation(file_path):
    # Load file content
    with open(file_path, 'r') as file:
        content = file.read()

    # Generate documentation using OpenAI GPT-4
    response = openai.Completion.create(
        engine="gpt-4",  # GPT-4 model
        prompt=f"Generate detailed documentation for the following code:\n\n{content}\n",
        max_tokens=1024,
        api_key=os.environ['OPENAI_API_KEY']
    )
    return response.choices[0].text

def main(changed_files):
    docs = {}
    for file_path in changed_files:
        if os.path.isfile(file_path):
            docs[file_path] = generate_documentation(file_path)
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
        doc_file_path = f"{file_path}.md"  # Assuming markdown format for docs
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
    changed_files = args.files
    openai_key = os.getenv("OPENAI_API_KEY", "")
    #documentation = main(changed_files)
    print(f"Changed files: {changed_files}, openai_key: {openai_key}")
