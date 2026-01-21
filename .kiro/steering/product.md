# Product Overview: LitheLauncher

## Product Name
LitheLauncher

## Overview
LitheLauncher is a Python-based game launcher application designed to provide users with a centralized and customizable platform for managing their game library. It allows users to view game details, launch games, execute commands before and after game launches, and synchronize save data.

## Core Features
- **Game Card List Display**: Ultra-responsive grid display of game entries, optimized for large libraries (5000+ games).
- **Asynchronous Image Processing**: Decoupled image decoding and scaling using dedicated thread pools to ensure smooth scrolling and zero UI lag.
- **Cover Art & Title Display**: High-performance display with visual loading indicators and placeholder support.
- **Pre/Post-Launch Commands**: Ability to specify and execute custom commands before and after launching a game, useful for mods, configurations, or external tools.
- **Smart Save Data Synchronization**: Automatically synchronizes game save data by comparing local and remote timestamps before and after launches. Includes conflict resolution UI for inconsistent data states.
- **Database Migration**: Automated code-first database migration system with backup and recovery protocols to ensure data integrity across application updates.
- **Game Detail Screen**: A dedicated screen to view and modify specific details for each game, including the executable path.
- **Logging Feature**: Comprehensive logging to both a file and the command line for tracking application 
activities and troubleshooting.
- **Internationalization (i18n)**: Full support for English and Japanese with real-time language switching and system locale auto-detection.
- **テスト自動化**: Pytest-qtを用いたGUIコンポーネントのテスト自動化

## Target Use Case
LitheLauncher targets PC gamers who seek more control and customization over their game library and launch process. It's particularly useful for users who:
- Have games from various sources and want a unified launcher.
- Utilize game mods, custom configurations, or third-party tools that require pre/post-launch execution.
- Desire automated save data management and synchronization.

## Key Value Proposition
LitheLauncher offers a flexible and powerful solution for game management, enhancing the user's gaming experience by:
- **Centralizing Game Management**: Consolidating diverse game libraries into one easy-to-use interface.
- **Automating Customization**: Simplifying the execution of complex pre/post-launch setups.
- **Ensuring Data Integrity**: Providing reliable save data synchronization and backup.
- **Improving User Experience**: Offering detailed game information and a clean interface.
