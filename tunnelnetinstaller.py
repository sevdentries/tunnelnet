
import platform 
system = platform.system()#OS CHECK STARTS HERE, should return "Windows", "Linux", or "Darwin" for MacOS.
#see official python documentation if confused.
#Nathan keep your code for the installscript inside an if statement checking variable system for OS thanks
print(system)
print("Install started")
if system == "Linux":
    import subprocess
    from pathlib import Path
    args = "linuxinstall.sh"
    print("Launching "+args+"...")
    parent = Path(__file__).resolve().parent
    assemblepath = str(parent / args)
    executable = f"sudo chmod +x {str(assemblepath)}"

    try:
        result = subprocess.run(f"{executable}", check=True, capture_output=True, text=True, shell=True)
        result = subprocess.run(f"sudo bash {assemblepath}", check=True, capture_output=True, text=True, shell=True)
        print(result.stdout)
    except subprocess.CalledProcessError as err:
        print("STDERR:", err.stderr)


