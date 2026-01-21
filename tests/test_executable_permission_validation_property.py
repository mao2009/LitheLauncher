"""
Property-based tests for executable path permission validation.
**Feature: game-execution-bug-fixes, Property 8: Executable path permission validation**
"""

import pytest
import tempfile
import os
import stat
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from src.executable_validator import ExecutableValidator, ValidationResult


# Strategy for generating files with different permission scenarios
@st.composite
def file_permission_strategy(draw):
    """Generate files with various permission configurations."""
    permission_type = draw(st.sampled_from(['readable_only', 'writable_only', 'executable', 'no_permissions', 'full_permissions']))
    file_extension = draw(st.sampled_from(['.exe', '.bat', '.cmd', '.sh', '.txt', '.py', '.com']))
    
    return {
        'permission_type': permission_type,
        'extension': file_extension
    }


@pytest.fixture
def permission_test_files():
    """Create temporary files with various permission configurations."""
    temp_dir = tempfile.mkdtemp()
    files = {}
    
    # Create files with different permissions
    permission_configs = [
        ('readable_only', stat.S_IRUSR),
        ('writable_only', stat.S_IWUSR),
        ('executable', stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR),
        ('no_permissions', 0),
        ('full_permissions', stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    ]
    
    extensions = ['.exe', '.bat', '.cmd', '.sh', '.txt', '.py', '.com']
    
    for perm_name, perm_mode in permission_configs:
        for ext in extensions:
            filename = f"{perm_name}_file{ext}"
            filepath = os.path.join(temp_dir, filename)
            
            # Create the file
            with open(filepath, 'w') as f:
                f.write(f"#!/bin/bash\necho 'Test file with {perm_name} permissions'")
            
            # Set permissions (only on Unix-like systems)
            if os.name != 'nt':
                os.chmod(filepath, perm_mode)
            
            files[f"{perm_name}_{ext[1:]}"] = filepath
    
    yield {
        'temp_dir': temp_dir,
        'files': files
    }
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@given(file_config=file_permission_strategy())
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_executable_path_permission_validation(permission_test_files, file_config):
    """
    **Feature: game-execution-bug-fixes, Property 8: Executable path permission validation**
    **Validates: Requirements 3.5**
    
    For any executable path validation, the system should verify both file existence 
    and executable permissions.
    """
    permission_type = file_config['permission_type']
    extension = file_config['extension'][1:]  # Remove the dot
    
    file_key = f"{permission_type}_{extension}"
    file_path = permission_test_files['files'].get(file_key)
    
    if not file_path:
        # Skip if file doesn't exist in our test setup
        return
    
    validator = ExecutableValidator()
    result = validator.validate_executable(file_path)
    
    # Verify that the result has proper structure
    assert isinstance(result, ValidationResult)
    assert isinstance(result.is_valid, bool)
    assert isinstance(result.error_type, str)
    assert isinstance(result.error_message, str)
    assert isinstance(result.suggested_action, str)
    
    # Determine expected validation result based on OS and file characteristics
    if os.name == 'nt':  # Windows
        # On Windows, validation depends on file extension
        executable_extensions = ['.exe', '.bat', '.cmd', '.com']
        if file_config['extension'] in executable_extensions:
            # Windows executable extensions should be considered valid regardless of permission bits
            if permission_type in ['executable', 'full_permissions', 'readable_only', 'writable_only']:
                assert result.is_valid, f"Windows executable with {extension} extension should be valid"
            elif permission_type == 'no_permissions':
                # Files with no permissions might still be considered valid on Windows if they have executable extensions
                # This depends on the specific implementation
                pass  # Allow either valid or invalid
        else:
            # Non-executable extensions should fail permission validation
            assert not result.is_valid, f"Non-executable extension {extension} should fail validation"
            assert result.error_type == "permission_denied"
            assert ("executable" in result.error_message.lower() or "permission" in result.error_message.lower())
    else:  # Unix-like systems
        # On Unix-like systems, check actual execute permissions
        if permission_type in ['executable', 'full_permissions']:
            # Files with execute permissions should be valid
            assert result.is_valid, f"File with execute permissions should be valid"
            assert result.error_type == ""
            assert result.error_message == ""
        else:
            # Files without execute permissions should fail
            assert not result.is_valid, f"File without execute permissions should fail validation"
            assert result.error_type == "permission_denied"
            assert "permission" in result.error_message.lower()
            assert result.suggested_action != ""


@given(st.lists(file_permission_strategy(), min_size=1, max_size=5))
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_permission_validation_consistency(permission_test_files, file_configs):
    """
    **Feature: game-execution-bug-fixes, Property 8: Executable path permission validation**
    **Validates: Requirements 3.5**
    
    For any set of files with different permissions, validation should be consistent
    and deterministic across multiple validation calls.
    """
    validator = ExecutableValidator()
    
    for file_config in file_configs:
        permission_type = file_config['permission_type']
        extension = file_config['extension'][1:]  # Remove the dot
        
        file_key = f"{permission_type}_{extension}"
        file_path = permission_test_files['files'].get(file_key)
        
        if not file_path:
            continue
        
        # Validate the same file multiple times
        result1 = validator.validate_executable(file_path)
        result2 = validator.validate_executable(file_path)
        result3 = validator.validate_executable(file_path)
        
        # All results should be identical
        assert result1.is_valid == result2.is_valid == result3.is_valid, \
            f"Validation consistency failed for {file_path}"
        assert result1.error_type == result2.error_type == result3.error_type, \
            f"Error type consistency failed for {file_path}"
        assert result1.error_message == result2.error_message == result3.error_message, \
            f"Error message consistency failed for {file_path}"
        assert result1.suggested_action == result2.suggested_action == result3.suggested_action, \
            f"Suggested action consistency failed for {file_path}"


def test_permission_validation_edge_cases(permission_test_files):
    """
    **Feature: game-execution-bug-fixes, Property 8: Executable path permission validation**
    **Validates: Requirements 3.5**
    
    Test edge cases for permission validation including empty paths, 
    non-existent files, and directories.
    """
    validator = ExecutableValidator()
    
    # Test empty path
    result = validator.validate_executable("")
    assert not result.is_valid
    assert result.error_type == "missing"
    
    # Test None path
    result = validator.validate_executable(None)
    assert not result.is_valid
    assert result.error_type == "missing"
    
    # Test whitespace-only path
    result = validator.validate_executable("   ")
    assert not result.is_valid
    assert result.error_type == "missing"
    
    # Test non-existent file
    result = validator.validate_executable("/nonexistent/path/file.exe")
    assert not result.is_valid
    assert result.error_type == "not_found"
    
    # Test directory instead of file
    result = validator.validate_executable(permission_test_files['temp_dir'])
    assert not result.is_valid
    assert result.error_type == "not_executable"
    assert "directory" in result.error_message.lower()


@given(st.text(min_size=1, max_size=200))
@settings(deadline=None)
def test_permission_validation_robustness(path):
    """
    **Feature: game-execution-bug-fixes, Property 8: Executable path permission validation**
    **Validates: Requirements 3.5**
    
    For any arbitrary path string, the validator should handle it gracefully
    without crashing and provide appropriate error information.
    """
    # Filter out paths that might cause issues with the test environment
    assume(not any(char in path for char in ['<', '>', '|', '*', '?', '"']))
    assume(len(path.strip()) > 0)
    
    validator = ExecutableValidator()
    
    try:
        result = validator.validate_executable(path)
        
        # Validator should always return a ValidationResult
        assert isinstance(result, ValidationResult)
        assert isinstance(result.is_valid, bool)
        assert isinstance(result.error_type, str)
        assert isinstance(result.error_message, str)
        assert isinstance(result.suggested_action, str)
        
        # If validation fails, there should be an error type and message
        if not result.is_valid:
            assert result.error_type in ["missing", "not_found", "not_executable", "permission_denied"]
            assert len(result.error_message) > 0
            assert len(result.suggested_action) > 0
        else:
            # If validation passes, error fields should be empty
            assert result.error_type == ""
            assert result.error_message == ""
            assert result.suggested_action == ""
            
    except Exception as e:
        # Validator should not raise exceptions for any input
        pytest.fail(f"Validator raised exception for path '{path}': {e}")


def test_cross_platform_permission_behavior(permission_test_files):
    """
    **Feature: game-execution-bug-fixes, Property 8: Executable path permission validation**
    **Validates: Requirements 3.5**
    
    Test that permission validation behaves appropriately across different platforms.
    """
    validator = ExecutableValidator()
    
    # Test with a .exe file (should be valid on Windows regardless of permission bits)
    exe_file = permission_test_files['files']['executable_exe']
    result = validator.validate_executable(exe_file)
    
    if os.name == 'nt':  # Windows
        # .exe files should generally be considered valid on Windows
        assert result.is_valid, "Executable .exe file should be valid on Windows"
    else:  # Unix-like
        # On Unix, it depends on the actual execute permissions
        # Since we set execute permissions for 'executable' files, it should be valid
        assert result.is_valid, "File with execute permissions should be valid on Unix"
    
    # Test with a .txt file (should fail on both platforms)
    txt_file = permission_test_files['files']['executable_txt']
    result = validator.validate_executable(txt_file)
    
    if os.name == 'nt':  # Windows
        # .txt files should fail on Windows (not executable extension)
        assert not result.is_valid, ".txt file should fail validation on Windows"
        assert result.error_type == "permission_denied"
    else:  # Unix-like
        # On Unix, .txt with execute permissions should actually be valid
        # (Unix doesn't care about extensions, only permission bits)
        assert result.is_valid, "File with execute permissions should be valid on Unix regardless of extension"