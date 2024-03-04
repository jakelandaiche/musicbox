from websockets.server import WebSocketServerProtocol as Socket

from dataclasses import dataclass, field


@dataclass(eq=False, frozen=False)
class Player:
    """
    A dataclass that holds fields for a Player, which is
    a member of a Room
    """

    websocket: Socket | None
    name: str

    color: str = "#000000"
    color_list: list[int] = field(default_factory=list)
    ready: bool = False
    answer: str | None = None
    score: int = 0
    total: int = 0
    db_id: str | None = None
    score_info = dict()
    unique_words = set()
    word_count = 0
    word_len = 0

    @property
    def connected(self):
        return self.websocket is not None

    def clear(self):
        self.answer = None
        self.score = 0
        self.color_list = []

    def to_obj(self):
        return {
            "name": self.name,
            "connected": self.connected,
            "color": self.color,
            "color_list": self.color_list,
            "ready": self.ready,
            "answer": self.answer,
            "score": self.score,
            "total": self.total,
            "db_id": self.db_id,
            "score_info": self.score_info,
            "unique_words": list(self.unique_words),
            "avg_len": self.word_len / self.word_count if self.word_count > 0 else 0,
        }


class PlayerManager:
    def __init__(self):
        pass
