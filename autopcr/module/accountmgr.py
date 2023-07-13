# 名字需要斟酌一下

from .modulebase import ModuleManager
import os, re
from typing import Dict, Iterator
from ..constants import CONFIG_PATH
from asyncio import Lock

class AccountException(Exception):
    pass

class Account(ModuleManager):
    def __init__(self, parent: 'AccountManager', account: str):
        if not account in parent.account_lock:
            parent.account_lock[account] = Lock()
        self._lck = parent.account_lock[account]
        self._account = account
        super().__init__(os.path.join(CONFIG_PATH, account) + '.json')
    
    async def __aenter__(self):
        await self._lck.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.save_config()
        self._lck.release()

class AccountManager:
    pathsyntax = re.compile(r'[a-zA-Z0-9_]{1,32}')
    def __init__(self, root: str):
        self.root = root
        self.account_lock: Dict[str, Lock] = {}
    
    def load(self, account: str) -> Account:
        if not AccountManager.pathsyntax.match(account):
            raise AccountException('Invalid account name')
        return Account(self, account)
    
    def accounts(self) -> Iterator[str]:
        for fn in os.listdir(self.root):
            if fn.endswith('.json'):
                yield fn[:-5]


instance = AccountManager(os.path.join(CONFIG_PATH))
