from fasthtml.common import (
    serve,
    FastHTML,
    Titled,
    RedirectResponse,
    Beforeware,
    SortableJS,
    MarkdownJS,
    Request,
)
from fasthtml.components import P, Div, Form, Input, Button
import database

login_redir = RedirectResponse("/login", status_code=303)


def auth(request: Request, sess) -> None | RedirectResponse:
    """Check if the user is logged in."""
    user = request.scope["username"] = sess.get("username", None)
    if not user:
        return login_redir
    return None


def not_found(request: Request, exc) -> object:
    """Our 404 page."""
    return Titled("Oh no!", Div("We could not find that page :("))


beforewares: list[Beforeware] = [
    Beforeware(
        auth, skip=[r"/favicon\.ico", r"/static/.*", r".*\.js", r".*\.css", "/login"]
    )
]

headers = (
    SortableJS(".sortable"),
    MarkdownJS(".markdown"),
)

app = FastHTML(
    before=beforewares, exception_handlers={404: not_found}, hdrs=headers, debug=True
)


@app.route("/login", methods=["GET"])
def get_login():
    """Show the login form."""
    frm = Form(action="/login", method="post")(
        Input(id="name", placeholder="Name"),
        Input(id="password", type="password", placeholder="Password"),
        Button("login"),
    )
    return Titled("Login", frm)


@app.route("/login", methods=["POST"])
def post_login(login: database.Login, session):
    """Log in the user."""
    if not login.name or not login.password:
        return login_redir
    try:
        user = login.login()
        if not user:
            user = login.register()
    except ValueError:
        return login_redir
    session["username"] = user.name
    return RedirectResponse("/", status_code=303)


@app.route("/", methods=["GET"])
def home(request: Request):
    """Main page for the application.

    Should show the leaderboard, and have buttons to quickly add a new game.
    Refs should be able to edit any game, players can only edit games they are involved in.
    Games can be "ended", at which point only the refs can edit them.
    """
    return Titled("Friend Olympics", Div(P(f"Hello {request.scope["username"]}!")))


if __name__ == "__main__":
    database.create_db()
    serve()
