import subprocess
import shlex

command_to_run = "apt update"

args = shlex.split(f"sudo {command_to_run}")

try:
    result = subprocess.run(args, check=True, capture_output=True, text=True)
    #print("STDOUT:", result.stdout)
    #print("STDERR:", result.stderr)
except subprocess.CalledProcessError as e:
    print(f"Command failed with return code {e.returncode}")
    print("STDOUT:", e.stdout)
    print("STDERR:", e.stderr)
except FileNotFoundError:
    print(f"Error: Command '{args[0]}' not found. Make sure it is in your PATH.")

