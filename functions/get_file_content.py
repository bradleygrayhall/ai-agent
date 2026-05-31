import os
from google.genai import types
from config import MAX_CHARS

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read and return the actual text content of a single file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="points directly to a file we want to read",
            ),
        },
        required=["file_path"]
    ),
)

def get_file_content(working_directory: str, file_path: str) -> str:
    try:
        working_dir = os.path.abspath(working_directory)
        target_file = os.path.abspath(os.path.join(working_dir, file_path))

        valid_target_file = os.path.commonpath([working_dir, target_file]) == working_dir

        if not valid_target_file:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(target_file, "r") as f:
            content = f.read(MAX_CHARS)

            if f.read(1):
                content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'

            return content

    except Exception as e:
        return f"Error: {e}"