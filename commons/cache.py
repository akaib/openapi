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

from time import time
from pydantic import BaseModel


TTL = 14400


class CacheItem(BaseModel):
    item: dict
    timestamp: float


class CacheModel(object):
    def __init__(self):
        self.cache = {}

    def set_item(self, key, value):
        self.cache[key] = CacheItem(item=value, timestamp=time())

    def get_item(self, key):
        if self.is_expired(key):
            self.del_item(key)
            return
        return self.cache.get(key)

    def del_item(self, key):
        if self.is_expired(key):
            return
        del self.cache[key]

    def is_expired(self, key):
        item = self.get_item(key)
        if not item:
            return True
        if time() - item.timestamp >= TTL:
            return True
        return False


