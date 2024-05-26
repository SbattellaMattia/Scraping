from enum import Enum


class Status(Enum):
    SUCCESS = 1,
    ERROR = 2,
    TIMEOUT = 3,
    RETRY = 4,


class WebPage:
    def __init__(self, url: str, depth: int = 1):
        self.url = url
        self.depth: int = depth
        self.status: Status | None = None
        self.code: int | None = None
        self.has_keyword: bool = False

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
