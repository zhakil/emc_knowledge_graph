"""
Utility Functions and Helper Methods for EMC Knowledge Graph System

This module provides essential utility functions, configuration management,
logging setup, and data validation helpers used throughout the EMC Knowledge
Graph System. These utilities support the core functionality while maintaining
clean separation of concerns.

Functions:
    load_config: Load configuration from YAML files
    setup_logging: Configure logging system
    validate_data_structure: Validate data structures
    ensure_directory: Create directories if they don't exist
    format_timestamp: Format datetime objects for display
    sanitize_filename: Clean filenames for file system compatibility

Author: EMC Standards Research Team
Version: 1.0.0
"""

import hashlib
import json
import logging
import logging.handlers
import os
import platform
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml

# Version information
__version__ = "1.0.0"


def load_config(config_path: Union[str, Path] = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file with fallback to defaults.

    This function loads application configuration from a YAML file and provides
    sensible defaults if the configuration file is not found or contains
    incomplete settings.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dict containing configuration settings

    Raises:
        FileNotFoundError: If config file is required but not found
        yaml.YAMLError: If config file contains invalid YAML
    """
    config_path = Path(config_path)

    # Default configuration
    default_config = {
        "project": {
            "name": "EMC Knowledge Graph System",
            "version": "1.0.0",
            "description": "Automotive Electronics EMC Standards Knowledge Graph",
        },
        "application": {
            "debug_mode": False,
            "log_level": "INFO",
            "max_workers": 4,
            "timeout_seconds": 30,
        },
        "graph": {
            "layout": {
                "default": "spring",
                "spring_k": 3,
                "spring_iterations": 50,
                "random_seed": 42,
            },
            "nodes": {"default_size": 1500, "font_size": 10},
            "edges": {"default_width": 2, "alpha": 0.6},
        },
        "visualization": {
            "static": {"figure_size": [20, 16], "dpi": 300, "format": "png"},
            "interactive": {"width": 1200, "height": 800, "format": "html"},
        },
        "output": {
            "directories": {
                "base": "output",
                "graphs": "output/graphs",
                "reports": "output/reports",
                "exports": "output/exports",
            }
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "files": {"main": "logs/emc_kg.log", "error": "logs/error.log"},
        },
    }

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                file_config = yaml.safe_load(f)

            if file_config:
                # Merge configurations with file config taking precedence
                config = _deep_merge_dict(default_config, file_config)
            else:
                config = default_config

        except yaml.YAMLError as e:
            logging.warning(f"Error loading config file {config_path}: {e}")
            logging.info("Using default configuration")
            config = default_config

    else:
        logging.info(f"Configuration file {config_path} not found, using defaults")
        config = default_config

    return config


def _deep_merge_dict(
    base_dict: Dict[str, Any], update_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.

    Args:
        base_dict: Base dictionary
        update_dict: Dictionary with updates

    Returns:
        Merged dictionary
    """
    result = base_dict.copy()

    for key, value in update_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dict(result[key], value)
        else:
            result[key] = value

    return result


def setup_logging(
    config: Optional[Dict[str, Any]] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Configure the logging system with appropriate handlers and formatters.

    This function sets up comprehensive logging for the EMC Knowledge Graph System,
    including console output, file logging, and error-specific logging.

    Args:
        config: Configuration dictionary containing logging settings
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Override log file path

    Returns:
        Configured logger instance
    """
    # Use provided config or load default
    if config is None:
        config = load_config()

    # Extract logging configuration
    log_config = config.get("logging", {})

    # Determine log level
    level = log_level or log_config.get("level", "INFO")
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create logs directory
    log_files = log_config.get("files", {})
    main_log_file = log_file or log_files.get("main", "logs/emc_kg.log")
    error_log_file = log_files.get("error", "logs/error.log")

    ensure_directory(Path(main_log_file).parent)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create formatter
    log_format = log_config.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    formatter = logging.Formatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler for all logs
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create file handler: {e}")

    # Error file handler
    try:
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    except Exception as e:
        print(f"Warning: Could not create error handler: {e}")

    # Create application-specific logger
    logger = logging.getLogger("emc_kg")
    logger.info(f"Logging initialized at level {level}")
    logger.info(f"Log file: {main_log_file}")

    return logger


def ensure_directory(directory_path: Union[str, Path]) -> Path:
    """
    Create directory and all parent directories if they don't exist.

    Args:
        directory_path: Path to directory to create

    Returns:
        Path object for the created directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_data_structure(
    data: Any, required_fields: List[str] = None, data_type: type = dict
) -> Tuple[bool, List[str]]:
    """
    Validate data structure against requirements.

    Args:
        data: Data to validate
        required_fields: List of required field names
        data_type: Expected data type

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check data type
    if not isinstance(data, data_type):
        errors.append(f"Expected {data_type.__name__}, got {type(data).__name__}")
        return False, errors

    # Check required fields for dictionary data
    if required_fields and isinstance(data, dict):
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif data[field] is None or (
                isinstance(data[field], str) and not data[field].strip()
            ):
                errors.append(f"Field '{field}' cannot be empty")

    is_valid = len(errors) == 0
    return is_valid, errors


def format_timestamp(dt: datetime, format_type: str = "default") -> str:
    """
    Format datetime object for display.

    Args:
        dt: Datetime object to format
        format_type: Type of formatting ('default', 'short', 'long', 'iso')

    Returns:
        Formatted datetime string
    """
    if dt is None:
        return "Unknown"

    formats = {
        "default": "%Y-%m-%d %H:%M:%S",
        "short": "%m/%d/%Y",
        "long": "%A, %B %d, %Y at %I:%M %p",
        "iso": "%Y-%m-%dT%H:%M:%S",
        "filename": "%Y%m%d_%H%M%S",
    }

    return dt.strftime(formats.get(format_type, formats["default"]))


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Clean filename for file system compatibility.

    Args:
        filename: Original filename
        max_length: Maximum filename length

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Remove multiple consecutive underscores
    sanitized = re.sub(r"_+", "_", sanitized)

    # Remove leading/trailing spaces and periods
    sanitized = sanitized.strip(" .")

    # Ensure not empty
    if not sanitized:
        sanitized = "untitled"

    # Truncate if too long
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        available_length = max_length - len(ext)
        sanitized = name[:available_length] + ext

    return sanitized


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = "md5") -> str:
    """
    Calculate hash of a file.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256')

    Returns:
        Hex digest of file hash
    """
    hash_obj = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging and logging.

    Returns:
        Dictionary containing system information
    """
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "architecture": platform.architecture(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "node": platform.node(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "current_directory": os.getcwd(),
        "path_separator": os.sep,
        "environment_variables": dict(os.environ),
    }


def memory_usage() -> Dict[str, float]:
    """
    Get current memory usage information.

    Returns:
        Dictionary with memory usage statistics
    """
    try:
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            "percent": process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024,
        }
    except ImportError:
        # Fallback if psutil not available
        import resource

        usage = resource.getrusage(resource.RUSAGE_SELF)
        return {
            "max_rss_mb": usage.ru_maxrss / 1024,  # May vary by platform
            "user_time": usage.ru_utime,
            "system_time": usage.ru_stime,
        }


def safe_json_serialize(obj: Any) -> str:
    """
    Safely serialize object to JSON with fallback for non-serializable objects.

    Args:
        obj: Object to serialize

    Returns:
        JSON string representation
    """

    def default_serializer(o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, set):
            return list(o)
        elif hasattr(o, "__dict__"):
            return o.__dict__
        else:
            return str(o)

    try:
        return json.dumps(obj, default=default_serializer, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Serialization error: {str(e)}"


def chunk_list(data_list: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size.

    Args:
        data_list: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [data_list[i : i + chunk_size] for i in range(0, len(data_list), chunk_size)]


def flatten_dict(
    d: Dict[str, Any], parent_key: str = "", sep: str = "."
) -> Dict[str, Any]:
    """
    Flatten nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys

    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def timing_decorator(func):
    """
    Decorator to measure function execution time.

    Args:
        func: Function to time

    Returns:
        Decorated function
    """
    import functools
    import time

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            logger = logging.getLogger(func.__module__)
            logger.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")

    return wrapper


def retry_on_exception(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry function on exception.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier for delay

    Returns:
        Decorator function
    """
    import functools
    import time

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger = logging.getLogger(func.__module__)
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay:.1f} seconds..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All retry attempts failed for {func.__name__}")
                        raise last_exception

            raise last_exception

        return wrapper

    return decorator


# Initialize module logger
logger = logging.getLogger(__name__)
