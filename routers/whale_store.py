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

import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from commons.cache import CacheModel, TTL


router = APIRouter()

VERSION = '1.0.0'
BASE_URL = 'https://store.whale.naver.com'


res_not_found = {
    'message': 'not found',
    'isError': True,
    'color': 'critical'
}

res_internal_error = {
    'message': 'server error',
    'isError': True,
    'color': 'critical'
}


cache = CacheModel()


class ShieldsEndpointSchema(BaseModel):
    schemaVersion: int = 1
    label: str = 'whale store'
    message: str
    color: str = 'blue'
    isError: bool = False
    cacheSeconds: int = TTL


@router.get(
    '/v/{item_id}',
    response_model=ShieldsEndpointSchema,
)
async def read_item(item_id: str):
    if not re.match(r'^[a-z]{32}$', item_id):
        return {'message': 'bad id', 'isError': True, 'color': 'critical'}

    item = cache.get_item(item_id)
    if not item:
        import httpx
        async with httpx.AsyncClient() as client:
            url = '%s/detail/%s' % (BASE_URL, item_id)
            r = await client.head(url)

            if r.status_code == httpx.codes.NOT_FOUND:
                return res_not_found
            # Save url as referer
            referer = url
            match = re.search(r'xsrf-token=([^;]+)',
                              r.headers.get('set-cookie'), re.I)
            if not match:
                return res_internal_error
            xsrf_token = match.group(1)

            from urllib.parse import urlparse
            headers = {
                'Host': urlparse(BASE_URL).netloc,
                'Accept': '*/*',
                'Accept-Language': 'ko',
                'Cookie': 'XSRF-TOKEN=%s' % (xsrf_token,),
                'Referer': referer,
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'X-XSRF-TOKEN': xsrf_token,
                'x-requested-with': 'XMLHttpRequest',
            }
            r = await client.get(
                '%s/ajax/extensions/%s?hl=ko' % (BASE_URL, item_id),
                headers=headers
            )

            if r.status_code == httpx.codes.NOT_FOUND:
                return res_not_found
        # Skipping chracters that causing syntax error
        text = r.text[r.text.index('{'):]

        import json
        try:
            j = json.loads(text)
        except json.decoder.JSONDecodeError as err:
            return res_internal_error
        version = j.get('version')
        item = {'message': 'v'+version}
        cache.set_item(item_id, item)
    return item

