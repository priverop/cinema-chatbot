import re
from dataclasses import dataclass, field

from app.domain.entities.chat_message import ChatResponse, ChatTurn
from app.domain.entities.guardrail_result import GuardrailResult
from app.domain.ports.guardrail import _allow
from app.domain.ports.movie_repository import MovieRepository

_PRICE_PATTERN = re.compile(r"(\d[\d.,]*\s*€|eur\b)", re.IGNORECASE)
_TIME_PATTERN = re.compile(r"\b\d{1,2}[h:]\d{2}\b")


@dataclass
class TitleLeakGuardrail:
    """Blocks replies that leak cinema data (prices, showtimes, movie titles).

    Mirrors OffTopicRefusal eval logic but sources titles from the live
    MovieRepository instead of the fixture sqlite.
    """

    movie_repository: MovieRepository
    _titles: list[str] = field(default_factory=list, init=False, repr=False)
    _titles_loaded: bool = field(default=False, init=False, repr=False)

    def _get_titles(self) -> list[str]:
        if not self._titles_loaded:
            movies = self.movie_repository.list_active()
            self._titles = [m.title for m in movies]
            self._titles_loaded = True
        return self._titles

    def check_input(self, message: str, history: list[ChatTurn]) -> GuardrailResult:
        return _allow("input")

    def check_output(self, message: str, response: ChatResponse) -> GuardrailResult:
        if response.tools_called:
            return _allow("output")
        text = response.reply or ""

        price_match = _PRICE_PATTERN.search(text)
        if price_match:
            return GuardrailResult(
                allowed=False,
                stage="output",
                category="off_topic_leak",
                reason=f"leaked price token: {price_match.group(0)!r}",
            )

        time_match = _TIME_PATTERN.search(text)
        if time_match:
            return GuardrailResult(
                allowed=False,
                stage="output",
                category="off_topic_leak",
                reason=f"leaked showtime token: {time_match.group(0)!r}",
            )

        text_lower = text.lower()
        for title in self._get_titles():
            if title.lower() in text_lower:
                return GuardrailResult(
                    allowed=False,
                    stage="output",
                    category="off_topic_leak",
                    reason=f"leaked movie title: {title!r}",
                )

        return _allow("output")
