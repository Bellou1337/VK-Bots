
class BaseParser:
    _urls: list[str] = []
    _index: int = 0
    _debug: bool

    def __init__(self, debug: bool = False) -> None:
        self._debug = debug
    
    def parse_image_urls(self, promt: list[str]):
        pass

    def get_image_url(self) -> str | None:
        if self._index >= len(self._urls):
            return None
        
        res = self._urls[self._index]
        self._index += 1
        return res