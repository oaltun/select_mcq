import typer
from typer import Typer


from yxlsx.cli import tex_select_exam2

app: Typer = typer.Typer()


app.add_typer(tex_select_exam2.app, name="tex_select_exam")


def yxlsx() -> None:
    app()


if __name__ == "__main__":
    app()
