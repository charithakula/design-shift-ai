import os

def update_env_variable(filepath: str, key: str, value: str) -> None:
    """
    Updates or adds a key-value pair in the .env file.

    Args:
        filepath (str): Path to the .env file.
        key (str): Environment variable name.
        value (str): New value to set.
    """
    lines = []
    # Check if the .env file exists, and read all lines if it does
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            lines = f.readlines()

    updated = False
    # Open the file for writing (this overwrites existing content)
    with open(filepath, "w") as f:
        for line in lines:
            # Look for the line starting with the key and replace it with new value
            if line.strip().startswith(f"{key}="):
                f.write(f"{key}={value}\n")
                updated = True
            else:
                # Write unchanged lines back
                f.write(line)
        # If key was not found, append it as a new line
        if not updated:
            f.write(f"{key}={value}\n")

    # Also update the environment variable in the current Python process
    os.environ[key] = value


def read_env_variable(key: str, default: str = "") -> str:
    """
    Reads an environment variable or returns a default if not found.

    Args:
        key (str): Environment variable name.
        default (str): Default value if the variable is not found.

    Returns:
        str: The value of the environment variable.
    """
    # Use os.getenv to fetch the environment variable or fallback to default
    return os.getenv(key, default)
