"""File I/O helper utilities."""

import hashlib
from pathlib import Path
from typing import Optional


def read_file(file_path: str | Path) -> str:
    """Read file contents as string.

    Args:
        file_path: Path to file

    Returns:
        File contents as string
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(file_path: str | Path, content: str) -> None:
    """Write content to file.

    Args:
        file_path: Path to file
        content: Content to write
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def ensure_dir(dir_path: str | Path) -> Path:
    """Ensure directory exists.

    Args:
        dir_path: Path to directory

    Returns:
        Path object for the directory
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def compute_hash(content: str) -> str:
    """Compute SHA256 hash of content.

    Args:
        content: Content to hash

    Returns:
        Hex digest of hash
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def file_exists(file_path: str | Path) -> bool:
    """Check if file exists.

    Args:
        file_path: Path to check

    Returns:
        True if file exists
    """
    return Path(file_path).exists()


def get_project_root() -> Path:
    """Get project root directory.

    Returns:
        Path to project root
    """
    # Assuming this file is in conversion/utils/
    return Path(__file__).parent.parent.parent


def get_rvo_components_dir() -> Path:
    """Get RVO components directory.

    Returns:
        Path to RVO components directory
    """
    # RVO is in a sibling directory to jinja-roos-components
    project_root = get_project_root()
    rvo_path = project_root.parent / "rvo" / "components"

    # Fallback to subdirectory if exists
    if not rvo_path.exists():
        rvo_path = project_root / "rvo" / "components"

    return rvo_path


def get_output_template_dir() -> Path:
    """Get output Jinja templates directory.

    Returns:
        Path to templates/components directory
    """
    return get_project_root() / "src" / "jinja_roos_components" / "templates" / "components"


def get_conversion_dir() -> Path:
    """Get conversion directory.

    Returns:
        Path to conversion directory
    """
    return get_project_root() / "conversion"
