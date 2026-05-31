import argparse
import os
import json
import re
import glob
import subprocess

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", required=True)
    parser.add_argument("filename", nargs="?")
    args = parser.parse_args()

    messages = [{"role": "user", "content": args.p}]
    if args.filename:
        messages.append({"role": "user", "content": args.filename})

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    def read_file(file_path):
        with open(file_path, "r") as file:
            content = file.read()
            return content

    def write_file(file_path, content):
        with open(file_path, "w") as file:
            file.write(content)
            return content

    def bash_command(command):
        result = subprocess.run(command.split(), capture_output=True, text=True)
        return result.stdout or result.stderr

    def edit_file(file_path, old_string, new_string):
        with open(file_path, "r") as file:
            content = file.read()
        content = content.replace(old_string, new_string)
        with open(file_path, "w") as file:
            file.write(content)
        return content

    def grep_content(pattern, path="."):
        matches = []
        for root, _, files in os.walk(path):
            for name in files:
                fp = os.path.join(root, name)
                try:
                    with open(fp) as f:
                        for i, line in enumerate(f, 1):
                            if re.search(pattern, line):
                                matches.append(f"{fp}:{i}:{line.rstrip()}")
                except (UnicodeDecodeError, OSError):
                    continue
        return "\n".join(matches) or "No matches"

    def glob_files(pattern):
        return "\n".join(glob.glob(pattern, recursive=True)) or "No matches"

    def list_directory(path="."):
        return "\n".join(sorted(os.listdir(path))) or "(empty)"

    def delete_file(file_path):
        os.remove(file_path)
        return f"Deleted {file_path}"

    def make_directory(path):
        os.makedirs(path, exist_ok=True)
        return f"Created {path}"

    TOOL_MAPPING = {
        "read": read_file,
        "write": write_file,
        "bash": bash_command,
        "edit": edit_file,
        "grep": grep_content,
        "glob": glob_files,
        "ls": list_directory,
        "delete": delete_file,
        "mkdir": make_directory,
    }

    while True:
        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "read",
                        "description": "Read and return the contents of a file",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path to the file to read",
                                }
                            },
                            "required": ["file_path"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "write",
                        "description": "Write content to a file",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path of the file to write to",
                                },
                                "content": {
                                    "type": "string",
                                    "description": "The content to write to the file",
                                },
                            },
                            "required": ["file_path", "content"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "bash",
                        "description": "Execute a shell command",
                        "parameters": {
                            "type": "object",
                            "required": ["command"],
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "The command to execute",
                                }
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "edit",
                        "description": "Replace an exact string in a file with a new string",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path to the file to edit",
                                },
                                "old_string": {
                                    "type": "string",
                                    "description": "The exact text to replace",
                                },
                                "new_string": {
                                    "type": "string",
                                    "description": "The text to replace it with",
                                },
                            },
                            "required": ["file_path", "old_string", "new_string"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "grep",
                        "description": "Search file contents for a regex pattern, returning matches as path:line:text",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "pattern": {
                                    "type": "string",
                                    "description": "The regex pattern to search for",
                                },
                                "path": {
                                    "type": "string",
                                    "description": "The directory to search in (defaults to current directory)",
                                },
                            },
                            "required": ["pattern"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "glob",
                        "description": "Find files matching a glob pattern (e.g. **/*.py)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "pattern": {
                                    "type": "string",
                                    "description": "The glob pattern to match files against",
                                }
                            },
                            "required": ["pattern"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "ls",
                        "description": "List the contents of a directory",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "The directory to list (defaults to current directory)",
                                }
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete",
                        "description": "Delete a file",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path to the file to delete",
                                }
                            },
                            "required": ["file_path"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "mkdir",
                        "description": "Create a directory (including parent directories)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "The directory path to create",
                                }
                            },
                            "required": ["path"],
                        },
                    },
                },
            ],
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")
        response = chat.choices[0].message
        if response.tool_calls is None:
            print(response.content)
            break

        messages.append(response)

        # TODO: Uncomment the following line to pass the first stage
        for tool in response.tool_calls or []:
            tool_name = tool.function.name
            tool_args = json.loads(tool.function.arguments)
            tool_response = TOOL_MAPPING[tool_name](**tool_args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool.id,
                    "content": tool_response,
                }
            )


if __name__ == "__main__":
    main()
