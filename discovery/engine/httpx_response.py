from discovery.engine.base_response import BaseResponse


class HTTPXResponse(BaseResponse):
    def __init__(self, response):
        self._response = response

    def __repr__(self):
        return f"Response(status={self.status}, url={self.url}, http_version={self.version})"

    @property
    def status(self) -> int:
        return int(self._response.status_code)

    @property
    def url(self) -> str:
        return str(self._response.url)

    @property
    def content_type(self) -> str:
        return str(self._response.headers["Content-Type"])

    @property
    def version(self) -> str:
        _, http_version = self._response.http_version.split("/")
        return f"{http_version}"

    @property
    def raw_response(self):
        return self._response

    async def json(self):
        return self._response.json()

    async def text(self):
        return self._response.text

    async def content(self) -> bytes:
        return bytes(self._response.content)
