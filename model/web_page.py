from enum import Enum


class Status(Enum):
    SUCCESS = 1,
    ERROR = 2,
    TIMEOUT = 3,
    RETRY = 4,
    NO_MORE_NEEDED =5,


class WebPage:
    def __init__(self, url: str, parent: 'WebPage' = None):
        self.url = url
        self.parent: WebPage | None = parent
        self.status: Status | None = None
        self.code: int | None = None
        self.has_keyword: bool = False

    @property
    def depth(self) -> int:
        return (self.parent.depth if self.has_parent else 0) + 1

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        """
        Check and fix any URLs that are incorrectly formatted
        """
        self._url = value.replace(' ', '').replace('http://', 'https://')
        if not self._url.startswith('https://'):
            self._url = f'https://{self._url}'
        if '.' not in self._url.replace('www.', ''):
            self._url += '.it'

    @property
    def is_done(self) -> bool:
        """Determines whether the request has been evaluated"""
        return type(self.status) is Status and self.status != Status.RETRY

    @property
    def has_error(self) -> bool:
        """Determines whether the request has been evaluated and the server answered unsuccessfully"""
        return type(self.code) is int and not 300 > self.code >= 200

    @property
    def has_parent(self) -> bool:
        return self.parent is not None
