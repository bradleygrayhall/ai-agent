import os
from google.genai import types
import subprocess

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="runs specifc python files",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to run",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional list of extra options"
            )
        },
        required=["file_path"]
    ),
)

def run_python_file(working_directory: str, file_path: str, args: list[str] | None = None) -> str:
    try:
        working_dir = os.path.abspath(working_directory)
        target_file = os.path.abspath(os.path.join(working_dir, file_path))

        valid_target_file = os.path.commonpath([working_dir, target_file]) == working_dir

        if not valid_target_file:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not target_file.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        command = ["python3",target_file]
        if args is not None:
            command.extend(args)
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=30,
            text=True,
            cwd=working_dir,
        )
        output_parts = []
        
        if result.returncode != 0:
            output_parts.append(f"Process exited with code {result.returncode}")
        if result.stdout:
            output_parts.append(f"STDOUT: {result.stdout}")

        if result.stderr:
            output_parts.append(f"STDERR: {result.stderr}")

        if not result.stdout and not result.stderr:
            output_parts.append("No output produced")
        return "\n".join(output_parts)
    except Exception as e:
        return f"Error: executing Python file: {e}"