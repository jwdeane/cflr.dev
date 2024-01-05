import typer

from cflr import sso

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)
app.add_typer(sso.app, name="sso", short_help="Toggle configured SSO email domains")

if __name__ == "__main__":
    app()
