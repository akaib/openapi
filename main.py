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
from routers.whale_store import router as whale_store
from routers.browser_headers import router as browser_headers


class CustomFastAPI(FastAPI):
    def include_router(self, router, **kwargs):
      prefix = kwargs.pop('prefix', '')
      super().include_router(router, prefix='/v1'+prefix, **kwargs)


app = CustomFastAPI()

@app.get('/', status_code=403)
async def read_root():
    return {'detail': 'Access Denied'}


app.include_router(
  whale_store,
  prefix='/whale-store',
  tags=['whale_store']
)

app.include_router(
  browser_headers,
  prefix='/browser-headers',
  tags=['browser_headers']
)


