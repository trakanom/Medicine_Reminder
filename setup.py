import os
import subprocess
import sys


def setup_venv():
    if not os.path.exists("venv"):
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])

    if sys.platform == "win32":
        activate_script = ".\\venv\\Scripts\\activate"
    else:
        activate_script = "./venv/bin/activate"

    return activate_script


def install_requirements():
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    )


def run_program():
    subprocess.check_call([sys.executable, "your_program.py"])


def main():
    activate_script = setup_venv()

    # Activate the virtual environment
    if sys.platform == "win32":
        activate_cmd = f"cmd.exe /k {activate_script}"
    else:
        activate_cmd = f"source {activate_script}"
    os.system(activate_cmd)

    install_requirements()
    run_program()


if __name__ == "__main__":
    main()
