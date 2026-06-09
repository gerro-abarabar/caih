import requests


def get_latest_version():
    """
    Checks the latest version of the project from a remote source.
    Returns True if the local version is up to date, False otherwise.
    """
    try:
        response = requests.get(
            "https://api.github.com/repos/gerro-abarabar/caih/releases/latest"
        )
        response.raise_for_status()
        latest_version = response.json().get("tag_name")
        return latest_version
    except requests.RequestException as e:
        print(f"Error checking project version: {e}")
        return True  # Assume up to date if there's an error
