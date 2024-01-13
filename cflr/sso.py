import os
import sys
from enum import StrEnum, auto

import httpx
import questionary
import typer
from rich import print, print_json
from rich.console import Console
from rich.table import Table

help = """
[bold]Toggle configured SSO email domain(s)[/bold]

:information_desk_person: [bold]Global API Key[/bold] authentication required for the [u]/accounts/:account_id/sso/v2/connectors[/u] endpoint.
https://developers.cloudflare.com/fundamentals/api/get-started/keys/#get-global-api-key-legacy
"""
app = typer.Typer(
    add_completion=False, help=help, no_args_is_help=True, rich_markup_mode="rich"
)

CLOUDFLARE_EMAIL = os.environ.get("CLOUDFLARE_EMAIL")
CLOUDFLARE_API_KEY = os.environ.get("CLOUDFLARE_API_KEY")
API_BASE_URL = "https://api.cloudflare.com/client/v4"
AUTH_HEADERS = {"x-auth-email": CLOUDFLARE_EMAIL, "x-auth-key": CLOUDFLARE_API_KEY}

if not CLOUDFLARE_EMAIL:
    print("Missing [bold red]CLOUDFLARE_EMAIL[/bold red] environment variable.")
    sys.exit(1)

if not CLOUDFLARE_API_KEY:
    print("Missing [bold red]CLOUDFLARE_API_KEY[/bold red] environment variable.")
    sys.exit(1)

if not CLOUDFLARE_EMAIL and not CLOUDFLARE_API_KEY:
    print("[red]Set required environment variables and try again[/red].")
    sys.exit(1)


class ConnectorStatus(StrEnum):
    DIS = auto()
    V = auto()


def _filter_sso_connectors(connectors: list, filter: ConnectorStatus):
    filtered_connectors = {}

    for connector in connectors:
        if connector["connector_status"] == filter.upper():
            filtered_connectors.update(
                {connector["email_domain"]: connector["connector_id"]}
            )

    return filtered_connectors


def _get_sso_connectors(account_id: str):
    r = httpx.get(
        f"{API_BASE_URL}/accounts/{account_id}/sso/v2/connectors", headers=AUTH_HEADERS
    ).raise_for_status()
    data = r.json()

    if not data["success"]:
        error = data["errors"][0]["message"]
        print(f"API error: [red]{error}[/red]")
        raise typer.Exit(1)

    return data["result"]


@app.command(name="disable")
def disable_sso(account_id: str, debug: bool = False):
    """
    Disable an SSO email domain
    """
    data = _get_sso_connectors(account_id)
    enabled_connectors = _filter_sso_connectors(data, filter=ConnectorStatus.V)

    if not enabled_connectors:
        print("No enabled connectors found. Exiting.")
        raise typer.Exit(1)

    email_domains = enabled_connectors.keys()
    sso_domain = questionary.select(
        message="What email domain would you like to disable", choices=email_domains
    ).ask()
    sso_id = enabled_connectors[sso_domain]

    r = httpx.patch(
        f"{API_BASE_URL}/accounts/{account_id}/sso/v2/connectors/{sso_id}",
        headers=AUTH_HEADERS,
        json={"sso_connector_status": "DIS"},
    ).raise_for_status()
    data = r.json()

    if debug:
        print_json(data=data)
        raise typer.Exit(1)

    print(
        f":sparkles: Success, SSO [bold red]disabled[/bold red] for [bold]{sso_domain}[/bold]"
    )


@app.command(name="enable")
def enable_sso(account_id: str, debug: bool = False):
    """
    Enable an SSO email domain
    """
    data = _get_sso_connectors(account_id)
    disabled_connectors = _filter_sso_connectors(data, filter=ConnectorStatus.DIS)

    if not disabled_connectors:
        print("No disabled connectors found. Exiting.")
        raise typer.Exit(1)

    email_domains = disabled_connectors.keys()
    sso_domain = questionary.select(
        message="What email domain would you like to enable", choices=email_domains
    ).ask()
    sso_id = disabled_connectors[sso_domain]

    r = httpx.patch(
        f"{API_BASE_URL}/accounts/{account_id}/sso/v2/connectors/{sso_id}",
        headers=AUTH_HEADERS,
        json={"sso_connector_status": "V"},
    ).raise_for_status()
    data = r.json()

    if debug:
        print_json(data=data)
        raise typer.Exit(1)

    print(
        f":sparkles: Success, SSO [bold green]enabled[/bold green] for [bold]{sso_domain}[/bold]"
    )


@app.command(name="list")
def list_sso_connectors(account_id: str, debug: bool = False):
    """
    List SSO email domains
    """
    data = _get_sso_connectors(account_id)

    if debug:
        print_json(data=data)
        raise typer.Exit(1)

    table = Table()
    table.add_column("ID", style="cyan")
    table.add_column("Email Domain", style="magenta")
    table.add_column("Status", style="green")

    for connector in data:
        if not connector["connector_status"] == "D":
            table.add_row(
                connector["connector_id"],
                connector["email_domain"],
                connector["connector_status"],
            )

    console = Console()
    console.print(table)


if __name__ == "__main__":
    app()
