from touchance.quant_bridge import TCore


class TradeAPI(TCore):
    port = '51207'

    async def get_accounts(self):
        return await self._send({'Request': 'ACCOUNTS', 'SessionKey': self.session_key})

    async def restore_report(self, qry_index):
        return await self._send({'Request': 'RESTOREREPORT', 'SessionKey': self.session_key, 'QryIndex': qry_index})

    async def new_order(self, param: dict):
        return await self._send({'Request': 'NEWORDER', 'SessionKey': self.session_key, 'Param': param})

    async def replace_order(self, param: dict):
        return await self._send({'Request': 'REPLACEORDER', 'SessionKey': self.session_key, 'Param': param})

    async def cancel_order(self, param: dict):
        return await self._send({'Request': 'CANCELORDER', 'SessionKey': self.session_key, 'Param': param})

    async def margins(self, account_mask: str):
        return await self._send({'Request': 'MARGINS', 'SessionKey': self.session_key, "AccountMask": account_mask})

    async def positions(self, account_mask: str, qry_index):
        return await self._send({
            "Request": "POSITIONS", "SessionKey": self.session_key, "AccountMask": account_mask, "QryIndex": qry_index
        })

    async def restore_fill_report(self, qry_index):
        return await self._send({'Request': 'RESTOREFILLREPORT', 'SessionKey': self.session_key, 'QryIndex': qry_index})
