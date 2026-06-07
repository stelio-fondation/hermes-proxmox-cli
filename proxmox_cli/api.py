import os
import click
from proxmoxer import ProxmoxAPI
from dotenv import load_dotenv

# Load .env for local development if present
load_dotenv()

def get_api_client():
    """
    Initializes and returns the Proxmox API client using environment variables.
    Expected variables:
    - PM_URL: https://<host>:<port>/api2/json
    - PM_USER: user@pam!tokenid
    - PM_TOKEN: secret
    - PM_VERIFY_SSL: true/false (default: true)
    """
    url = os.getenv("PM_URL")
    user = os.getenv("PM_USER")
    token = os.getenv("PM_TOKEN")
    verify_ssl = os.getenv("PM_VERIFY_SSL", "true").lower() == "true"

    if not all([url, user, token]):
        raise click.ClickException(
            "Missing environment variables for Proxmox authentication. "
            "Please ensure PM_URL, PM_USER, and PM_TOKEN are set."
        )

    try:
        # Parse PM_USER: expected format "user@realm!tokenid"
        if "!" in user:
            user_name, token_name = user.split("!", 1)
        else:
            user_name = user
            token_name = None

        return ProxmoxAPI(
            url,
            user=user_name,
            token_name=token_name,
            token_value=token,
            verify_ssl=verify_ssl
        )
    except Exception as e:
        raise click.ClickException(f"Error connecting to Proxmox API: {e}")
