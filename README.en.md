# LitheLauncher

LitheLauncher is a high-performance game launcher developed in Python (PySide6), designed for speed and responsiveness. Even with a massive library of over 5,000 games, it launches in a staggering **0.12 seconds** and provides a butter-smooth scrolling experience thanks to advanced asynchronous image decoding.

## Key Features

-   **Ultra-Fast Startup & Async Loading**: Instantly launches and loads game data sequentially in the background without blocking the UI, even with 5,000+ entries.
-   **Advanced Async Image Processing**: Offloads image decoding and scaling to a dedicated thread pool (`ImagePool`), ensuring zero lag during scrolling.
-   **Virtualizing Grid Display**: Uses `WidgetPool` for widget reuse and virtualization, enabling high-speed rendering of massive lists with minimal memory overhead.
-   **Pre/Post-Launch Commands**: Execute custom shell commands before or after launching games—perfect for mods and custom setups.
-   **Smart Save Data Sync**: Automatically synchronizes save files by comparing local/remote timestamps, featuring a built-in conflict resolution UI.
-   **Code-First DB Migration**: Ensures data integrity with automated backups and recovery protocols during schema updates.
-   **Internationalization (i18n)**: Full support for English and Japanese with real-time switching and auto-detection.
-   **Test Automation**: Comprehensive automated testing using `pytest-qt` and `Hypothesis`.

## Target Audience

LitheLauncher is built for power users with massive game libraries who demand a fast, lightweight, and customizable management tool.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- PySide6

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/lithelauncher.git
   cd lithelauncher
   ```
2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```
3.  **Activate the virtual environment**:
    -   **Windows**:
        ```bash
        .\venv\Scripts\activate
        ```
    -   **macOS/Linux**:
        ```bash
        source venv/bin/activate
        ```
4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Launching the Application

After installation, activate your virtual environment and run:

```bash
python main.py
```

### Adding Games

1.  Click the "Add Game" button.
2.  Fill in the game details, including the executable path.
3.  Optionally, set pre/post-launch commands and save data synchronization settings.
4.  Save the game.

### Pre/Post-Launch Commands

You can configure commands to run before a game launches (e.g., to activate a mod) or after a game closes (e.g., to backup a specific file).

1.  Edit game details.
2.  Enter your desired commands in the "Pre-Launch Command" and "Post-Launch Command" fields.
3.  Commands are executed using the system shell. Ensure they are valid for your OS.

### Save Data Synchronization

Enable save data synchronization in game details to automatically upload/download save files to/from a remote location.

1.  Enable "Sync Save Data".
2.  Specify the local "Save Folder" and "Remote Sync Path".
3.  Before launching, save data will be downloaded; after closing, it will be uploaded.

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Running Tests

To run the automated tests, activate your virtual environment and execute:

```bash
pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.