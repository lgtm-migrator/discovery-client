from discovery.api.abc import Api


class Area(Api):
    def __init__(self, endpoint: str = "/operator/area", **kwargs):
        super().__init__(endpoint=endpoint, **kwargs)

    async def create(self, data, **kwargs):
        response = await self.client.post(f"{self.url}", data=data, params=kwargs)
        return response

    async def list(self, uuid=None, **kwargs):
        if uuid:
            uri = f"{self.url}/{uuid}"
        else:
            uri = f"{self.url}"
        response = await self.client.get(uri, params=kwargs)
        return response

    async def update(self, uuid, data, **kwargs):
        response = await self.client.put(f"{self.url}/{uuid}", params=kwargs, data=data)
        return response

    async def delete(self, uuid, **kwargs):
        response = await self.client.delete(f"{self.url}/{uuid}", params=kwargs)
        return response

    async def join(self, uuid, data, **kwargs):
        response = await self.client.put(
            f"{self.url}/{uuid}/join", params=kwargs, data=data
        )
        return response

    async def members(self, uuid, **kwargs):
        response = await self.client.get(f"{self.url}/{uuid}/members", params=kwargs)
        return response
