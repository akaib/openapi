# Copyright (C) 2020 Xvezda <xvezda@naver.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from routers.whale_store import router as whale_store
from routers.browser_headers import router as browser_headers
from routers.ip_address import router as ip_address


NAME = 'Akaib OpenAPI'
VERSION = '1.0.3'


class CustomFastAPI(FastAPI):
    prefix = '/v1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **dict(kwargs, docs_url=None, redoc_url=None))

    def get_prefix(self):
        return self.prefix

    def include_router(self, router, **kwargs):
        prefix = kwargs.pop('prefix', '')
        super().include_router(router,
                               prefix=self.prefix+prefix,
                               **kwargs)


app = CustomFastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)

app.include_router(
    whale_store,
    prefix='/whale-store',
)

app.include_router(
    browser_headers,
    prefix='/browser-headers',
)

app.include_router(
    ip_address,
    prefix='/ip-address',
)


@app.get('/')
async def redirect_root():
    return RedirectResponse(app.get_prefix())


@app.get(app.get_prefix())
async def show_oas():
    return get_openapi(title=NAME, version=VERSION, routes=app.routes)


