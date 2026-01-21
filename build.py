import subprocess
import platform
import shutil
import os
import sys

APP_NAME = "LitheLauncher"
MAIN_SCRIPT = "main.py"
ICON_PATH = "res/icon.png"
ADD_DATA_PATHS = [
    "res",
    "LICENSE",
    "NOTICE.md"
]
HIDDEN_IMPORTS = [
    "shlex",
    "uuid",
    "sqlite3",
    "PIL.Image",
    "Pillow" # Pillow モジュール全体も隠しインポート
]

def clean_build_dirs():
    """Cleans up the build and dist directories."""
    print("Cleaning up build and dist directories...")
    dirs_to_remove = ["build", "dist"]
    for d in dirs_to_remove:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
            except PermissionError:
                print(f"Warning: Could not remove {d} directory. Is the application still running?")
            except Exception as e:
                print(f"Warning: Could not remove {d}: {e}")
    
    spec_file = f"{APP_NAME}.spec"
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
        except Exception as e:
            print(f"Warning: Could not remove {spec_file}: {e}")
    print("Clean up complete.")

def build_windows():
    """Builds the application for Windows split files."""
    print("Building for Windows...")
    command = [
        "pyinstaller",
        MAIN_SCRIPT,
        "--onedir",
        "--windowed",
        f"--icon={ICON_PATH}",
        f"--name={APP_NAME}"
    ]
    for path in ADD_DATA_PATHS:
        command.append(f"--add-data={path};.") # Copy to root of dist folder
    for module in HIDDEN_IMPORTS:
        command.append(f"--hidden-import={module}")

    try:
        subprocess.run(command, check=True)
        print(f"Windows build successful! Application in ./dist/{APP_NAME}/")
    except subprocess.CalledProcessError as e:
        print(f"Windows build failed: {e}")
        sys.exit(1)

def build_macos():
    """Builds the application for macOS split files."""
    print("Building for macOS...")
    command = [
        "pyinstaller",
        MAIN_SCRIPT,
        "--onedir",
        "--windowed",
        f"--icon={ICON_PATH}",
        f"--name={APP_NAME}"
    ]
    for path in ADD_DATA_PATHS:
        command.append(f"--add-data={path}:.") # Copy to root of app bundle/dir
    for module in HIDDEN_IMPORTS:
        command.append(f"--hidden-import={module}")

    try:
        subprocess.run(command, check=True)
        print(f"macOS build successful! Application in ./dist/{APP_NAME}/")
    except subprocess.CalledProcessError as e:
        print(f"macOS build failed: {e}")
        sys.exit(1)

def build_linux():
    """Builds the application for Linux split files."""
    print("Building for Linux...")
    command = [
        "pyinstaller",
        MAIN_SCRIPT,
        "--onedir",
        "--windowed",
        f"--icon={ICON_PATH}", # Linux often uses .png or .ico for window icons
        f"--name={APP_NAME}"
    ]
    for path in ADD_DATA_PATHS:
        command.append(f"--add-data={path}:.") # Copy to root of dist folder
    for module in HIDDEN_IMPORTS:
        command.append(f"--hidden-import={module}")

    try:
        subprocess.run(command, check=True)
        print(f"Linux build successful! Executable in ./dist/{APP_NAME}")
    except subprocess.CalledProcessError as e:
        print(f"Linux build failed: {e}")
        sys.exit(1)

def main():
    clean_build_dirs()
    current_os = platform.system()
    if current_os == "Windows":
        build_windows()
    elif current_os == "Darwin": # macOS
        build_macos()
    elif current_os == "Linux":
        build_linux()
    else:
        print(f"Unsupported operating system: {current_os}")
        sys.exit(1)

if __name__ == "__main__":
    main()
