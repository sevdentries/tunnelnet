'''
command for docker testing:

docker run -it --rm \
  --cap-add=NET_ADMIN \
  --device=/dev/net/tun \
  -v "$(pwd)":/workspace \
  tailscale
  bash -lc "cd workspace/Documents/GitHub/meshmilk"

Dockerfile:

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    curl \
    iproute2 \
    ca-certificates \
    git \
    sudo

CMD ["bash"]

build using docker build -t (NAME) (PATH towards Dockerfile)

and final clone script

git clone https://github.com/sevdentries/meshmilk.git
'''
import platform 
system = platform.system()#OS CHECK STARTS HERE, should return "Windows", "Linux", or "Darwin" for MacOS.
#see official python documentation if confused.
#Nathan keep your code for the installscript inside an if statement checking variable system for OS thanks

if system == "Linux":
    import subprocess
    import shlex
    from pathlib import Path

    command_to_run = "echo \"hello is this thing working\""

    args = "linuxinstall.sh"
    parent = Path(__file__).resolve().parent
    assemblepath = str(parent / args)
    executable = f"sudo chmod +x {str(assemblepath)}"

    try:
        result = subprocess.run(f"{executable}", check=True, capture_output=True, text=True, shell=True)
        result = subprocess.run(f"sudo bash {assemblepath}", check=True, capture_output=True, text=True, shell=True)
        print(result.stdout)
    except subprocess.CalledProcessError as err:
        print("STDERR:", err.stderr)


