import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)

def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        path = os.path.abspath(working_directory)
        target_dir = os.path.abspath(os.path.join(path, directory))

        valid_target_dir = os.path.commonpath([path, target_dir]) == path
        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        files_info = []

        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)

            file_size = os.path.getsize(item_path)
            is_dir = os.path.isdir(item_path)

            files_info.append(
                f"- {item}: file_size={file_size} bytes, is_dir={is_dir}"
            )

        return "\n".join(files_info)

    except Exception as e:
        return f"Error: {e}"