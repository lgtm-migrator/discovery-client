from discovery.api.abc import Api


class Role(Api):
    def __init__(self, endpoint: str = "/acl/role", **kwargs):
        super().__init__(endpoint=endpoint, **kwargs)

    async def create(self, data, **kwargs):
        response = await self.client.put(f"{self.url}", params=kwargs, data=data)
        return response

    async def read_by_id(self, role_id, **kwargs):
        response = await self.client.put(f"{self.url}/{role_id}", params=kwargs)
        return response

    async def read_by_name(self, name, **kwargs):
        response = await self.client.put(f"{self.url}/name/{name}", params=kwargs)
        return response

    async def update(self, role_id, data, **kwargs):
        response = await self.client.put(
            f"{self.url}/{role_id}", params=kwargs, data=data
        )
        return response

    async def delete(self, role_id, **kwargs):
        response = await self.client.delete(f"{self.url}/{role_id}", params=kwargs)
        return response

    async def list(self, **kwargs):
        response = await self.client.get(f"{self.url}s", params=kwargs)
        return response
