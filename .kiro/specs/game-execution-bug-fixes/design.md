# Design Document

## Overview

This design addresses critical bugs in the LitheLauncher Game Launcher's game execution system. The current implementation suffers from ID mapping issues, improper subprocess handling, insufficient validation, and poor error reporting. The solution involves fixing the game ID propagation, implementing robust subprocess execution, adding comprehensive validation, and improving error handling throughout the launch pipeline.

## Architecture

The game execution system follows a layered architecture:

1. **UI Layer**: Game cards and dialogs that trigger launch requests
2. **Service Layer**: LauncherService that orchestrates the launch process
3. **Repository Layer**: GameRepository that provides game data
4. **System Layer**: Subprocess execution and file system validation

The fix will address issues at each layer while maintaining the existing architectural boundaries.

## Components and Interfaces

### GameCardWidget (UI Layer)
- **Current Issue**: Uses `game_id` field from game data, but database returns `id` field
- **Fix**: Standardize on `id` field consistently throughout the system
- **Interface**: Emits `launched(int game_id)` signal with correct ID

### LauncherService (Service Layer)
- **Current Issue**: Improper subprocess execution with `shell=True` and list arguments
- **Fix**: Use proper subprocess parameters based on operating system
- **Interface**: `launch_game(game_id: int) -> bool` with comprehensive error handling

### GameRepository (Repository Layer)
- **Current Issue**: Inconsistent field naming between database and application
- **Fix**: Ensure consistent field mapping in all database operations
- **Interface**: Return game data with standardized field names

### ExecutableValidator (New Component)
- **Purpose**: Centralized validation of executable paths and permissions
- **Interface**: `validate_executable(path: str) -> ValidationResult`

## Data Models

### Game Data Structure
```python
{
    "id": int,                    # Standardized ID field
    "title": str,
    "executable_path": str,       # Required for launch
    "description": str,
    "cover_art_path": str,
    "pre_command": str,
    "post_command": str,
    "save_folder": str,
    "sync_enabled": int,
    "remote_sync_path": str
}
```

### ValidationResult Structure
```python
{
    "is_valid": bool,
    "error_type": str,           # "missing", "not_found", "not_executable", "permission_denied"
    "error_message": str,
    "suggested_action": str
}
```

### LaunchResult Structure
```python
{
    "success": bool,
    "error_type": str,           # "validation", "subprocess", "command", "sync"
    "error_message": str,
    "process_info": dict
}
```

## 
Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Property 1: Game ID consistency in launch pipeline
*For any* game in the database, when a user double-clicks its game card, the launcher service should receive the exact same game ID that was stored in the database
**Validates: Requirements 1.1, 5.1, 5.2**

Property 2: Executable path validation before launch
*For any* game launch attempt, if the game has an executable path set, the system should validate the file exists before attempting subprocess execution
**Validates: Requirements 1.2, 3.1**

Property 3: Successful launch logging consistency
*For any* game with a valid executable path, when launched successfully, the system should log both the launch initiation and process completion
**Validates: Requirements 1.4, 1.5**

Property 4: Error message specificity for subprocess failures
*For any* subprocess execution failure, the system should capture and display the specific system error that caused the failure
**Validates: Requirements 2.3, 4.5**

Property 5: Command execution error reporting
*For any* pre-launch or post-launch command that fails, the system should display both the command that failed and the specific error details
**Validates: Requirements 2.4**

Property 6: Save data sync error handling
*For any* save data synchronization failure, the system should display sync-specific error information that identifies the sync direction and cause
**Validates: Requirements 2.5**

Property 7: Visual indication of invalid executables
*For any* game displayed in the library, if the executable path is missing or invalid, the game card should provide a visual indicator of this state
**Validates: Requirements 3.3**

Property 8: Executable path permission validation
*For any* executable path validation, the system should verify both file existence and executable permissions
**Validates: Requirements 3.5**

Property 9: Cross-platform subprocess execution
*For any* game launch, the subprocess execution should use appropriate parameters for the current operating system
**Validates: Requirements 4.1**

Property 10: Path handling with spaces
*For any* executable path containing spaces, the launcher service should handle path quoting correctly to ensure successful execution
**Validates: Requirements 4.2**

Property 11: Working directory management
*For any* game that requires a specific working directory, the launcher service should set the working directory appropriately before execution
**Validates: Requirements 4.3**

Property 12: Absolute and relative path handling
*For any* executable path (absolute or relative), the launcher service should resolve and execute the path correctly
**Validates: Requirements 4.4**

Property 13: Database ID field consistency
*For any* database query that returns game data, the system should use consistent field names for game identification across all components
**Validates: Requirements 5.4**

Property 14: Launch request ID validation
*For any* launch request received by the launcher service, the system should validate that the game ID exists in the database before proceeding
**Validates: Requirements 5.3**

Property 15: Operation logging with correct IDs
*For any* game operation that is logged, the log entry should include the correct game ID for traceability
**Validates: Requirements 5.5**

## Error Handling

### Error Categories

1. **Validation Errors**
   - Missing executable path
   - Non-existent executable file
   - Insufficient file permissions
   - Invalid game ID

2. **Subprocess Errors**
   - Process creation failure
   - Process execution failure
   - Working directory access issues
   - Path resolution problems

3. **Command Execution Errors**
   - Pre-launch command failures
   - Post-launch command failures
   - Command timeout issues
   - Command permission problems

4. **Synchronization Errors**
   - Save data download failures
   - Save data upload failures
   - Remote storage connectivity issues
   - Local file system access problems

### Error Handling Strategy

- **Fail Fast**: Validate all preconditions before attempting execution
- **Specific Messages**: Provide detailed error messages that help users understand and fix problems
- **Graceful Degradation**: Continue with available functionality when non-critical operations fail
- **Comprehensive Logging**: Log all errors with sufficient detail for debugging
- **User Guidance**: Provide actionable suggestions for resolving errors

## Testing Strategy

### Unit Testing Approach

Unit tests will focus on individual components and their specific responsibilities:

- **GameCardWidget**: Test ID emission and signal handling
- **LauncherService**: Test launch orchestration and error handling
- **ExecutableValidator**: Test validation logic for various file states
- **Subprocess execution**: Test process creation with various parameters

### Property-Based Testing Approach

Property-based tests will verify universal behaviors across all valid inputs:

- **ID Consistency**: Generate random games and verify ID propagation
- **Path Validation**: Generate various path formats and verify validation
- **Error Handling**: Generate error conditions and verify appropriate responses
- **Subprocess Execution**: Generate various executable configurations and verify proper handling

The property-based testing library **Hypothesis** will be used for Python, configured to run a minimum of 100 iterations per property test. Each property-based test will be tagged with a comment explicitly referencing the correctness property from this design document using the format: '**Feature: game-execution-bug-fixes, Property {number}: {property_text}**'

Each correctness property will be implemented by a single property-based test, ensuring comprehensive coverage of the system's expected behaviors across all valid inputs.
