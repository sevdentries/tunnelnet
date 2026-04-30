
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

elif system == "Darwin":
    import subprocess
    print("Detected macOS. Checking for Tailscale...")
    # Tailscale install for Mac often uses Homebrew or the App Store.
    # We will attempt the official install script which supports macOS.
    try:
        install_cmd = "curl -fsSL https://tailscale.com/install.sh | sh"
        print(f"Running: {install_cmd}")
        subprocess.run(install_cmd, shell=True, check=True)
        print("Tailscale installation attempt finished.")
        
        # Install python-tk to ensure Tk 8.6+ is available on macOS
        print("Installing python-tk to provide Tkinter 8.6+...")
        tk_install_cmd = "brew install python-tk"
        print(f"Running: {tk_install_cmd}")
        subprocess.run(tk_install_cmd, shell=True, check=False)
        print("Tkinter installation attempt finished.")
    except Exception as e:
        print(f"Error during Mac installation: {e}")

elif system == "Windows":
    import subprocess
    print("Detected Windows. Please ensure you are running as Administrator.")
    # On Windows, we typically download the MSI or use winget
    try:
        # Use winget if available
        print("Attempting to install Tailscale via winget...")
        subprocess.run("winget install Tailscale.Tailscale", shell=True, check=True)
        print("Tailscale installation via winget finished.")
    except Exception:
        print("winget failed or not found. Please download Tailscale from https://tailscale.com/download/windows")
else:
    print(f"Unsupported system: {system}")

