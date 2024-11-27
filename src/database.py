import sqlmodel
import uuid
import pydantic
import bcrypt
import datetime

db = sqlmodel.create_engine("sqlite:///db.sqlite")


class User(sqlmodel.SQLModel, table=True):
    """A user."""

    id: uuid.UUID = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = sqlmodel.Field(max_length=100, unique=True)
    hash: str
    score: int = sqlmodel.Field(default=0)


class Login(pydantic.BaseModel):
    """Payload supplied to log in."""

    name: str
    password: str

    def login(self) -> User | None:
        """Log in the user."""
        with sqlmodel.Session(db) as session:
            select = sqlmodel.select(User).where(User.name == self.name)
            user = session.exec(select).first()
            if not user:
                return None
            if not bcrypt.checkpw(
                self.password.encode("utf-8"), user.hash.encode("utf-8")
            ):
                raise ValueError("Incorrect password.")
            return user

    def register(self) -> User:
        """Register a new user."""
        with sqlmodel.Session(db) as session:
            select = sqlmodel.select(User).where(User.name == self.name)
            if session.exec(select).first():
                raise ValueError("User already exists.")
            user = User(
                name=self.name,
                hash=bcrypt.hashpw(
                    self.password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8"),
            )
            session.add(user)
            session.commit()
            return user


class Game(sqlmodel.SQLModel, table=True):
    """A game to play."""

    id: uuid.UUID = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = sqlmodel.Field(
        max_length=100, unique=True, description="The name of the game."
    )
    ranked: bool = sqlmodel.Field(
        default=False, description="Whether this game is ranked or win/lose."
    )
    importance: float = sqlmodel.Field(
        default=0.5, gt=0, lt=1, description="The k-value used in ELO calculations."
    )
    decay: float = sqlmodel.Field(
        default=2.0,
        gt=0,
        lt=10,
        description="The decay rate for ranked ELO calculations.",
    )


class Match(sqlmodel.SQLModel, table=True):
    """A match between two or more players."""

    id: uuid.UUID = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    game: uuid.UUID = sqlmodel.Field(foreign_key="game.id")
    started: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.now)
    finished: datetime.datetime = sqlmodel.Field(default=None)

    def compute_elo_updates(self) -> dict[uuid.UUID, float]:
        """Compute ELO updates for every player in the match."""
        with sqlmodel.Session(db) as session:
            select = sqlmodel.select(Result).where(Result.match == self.id)
            results = session.exec(select).all()
            game = session.get_one(Game, self.game)
            ranks = {result.rank: result.player for result in results}
            current_scores = {result.player: session.get_one(User, result.player).score for result in results}
            updates = {}
            for rank_one, player_one in ranks.items():
                for rank_two, player_two in ranks.items():
                    if player_one == player_two:
                        continue
                    prob_one = 1 / (1 + 10 ** ((current_scores[player_one] - current_scores[player_two]) / 400))
                    prob_two = 1 / (1 + 10 ** ((current_scores[player_two] - current_scores[player_one]) / 400))
                    updates[player_one] = game.importance * (rank_one > rank_two - prob_one)
                    updates[player_two] = game.importance * (rank_two > rank_one - prob_two)
            return updates


class Result(sqlmodel.SQLModel, table=True):
    """Players in a match."""
    id: uuid.UUID = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    match: uuid.UUID = sqlmodel.Field(foreign_key="match.id")
    player: uuid.UUID = sqlmodel.Field(foreign_key="user.id")
    rank: int = sqlmodel.Field(default=0)


def create_db() -> None:
    """Create a database if it doesn't exist."""
    sqlmodel.SQLModel.metadata.create_all(db)
