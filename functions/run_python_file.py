import os
import subprocess

from google.genai import types

def run_python_file(working_directory, file_path, args=None):
    try:
        
        working_directory_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_directory_abs, file_path))
        valid_target_dir = os.path.commonpath([working_directory_abs, target_file]) == working_directory_abs

        if not valid_target_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not str(target_file).endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", target_file]
        if args != None:
            command.extend(args)
        
        result = subprocess.run(
            command,
            cwd=working_directory_abs,
            capture_output=True,
            text=True,
            timeout=30            
        )

        output = ""
        if result.returncode != 0:
            output += f"Process exited with code {result.returncode}\n"
        if not result.stdout and not result.stderr:
            output += "No output produced"
        else:
            if result.stdout:
                output += f"STDOUT: {result.stdout}"
            if result.stderr:
                output += f"STDERR: {result.stderr}"
        
        return output
        
    except Exception as e:
        return f"Error: executing Python file: {e}"

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a specified Python file within the working directory and returns its output",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to run, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                ),
                description="Optional list of arguments to pass to the Python script",
            ),
        },
        required=["file_path"],
    ),
)