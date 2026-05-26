import argparse
import os
import sys
import json

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", required=True)
    parser.add_argument("filename", nargs='?')
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

    TOOL_MAPPING = {"read": read_file}

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
            }
        ],
    )

    if not chat.choices or len(chat.choices) == 0:
        raise RuntimeError("no choices in response")

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!", file=sys.stderr)

    # TODO: Uncomment the following line to pass the first stage
    response = False
    for tool in chat.choices[0].message.tool_calls:
        tool_name = tool.function.name
        tool_args = json.loads(tool.function.arguments)
        tool_response = TOOL_MAPPING[tool_name](**tool_args)
        response = tool_response
    if not response:
        response = chat.choices[0].message.content

    print(response)


if __name__ == "__main__":
    main()
