import asyncio
import logging
import aiohttp
import names
import websockets
from websockets import WebSocketServerProtocol, WebSocketProtocolError

logging.basicConfig(level=logging.INFO)


async def get_exchange():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5') as respon:
            if respon.status == 200:
                r = await respon.json()
                exc, = list(filter(lambda el: el['ccy'] == 'USD', r))
            return F"USD: buy: {exc['buy']}, sale: {exc['sale']}"


class Server:
    clients = set()

    async def reg(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name
        self.clients.add(ws)
        logging.info(F"{ws.remote_address} connects")
    
    async def unreg(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message):
        if self.clients:
            [await client.send(message) for client in self.clients]
    
    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.reg(ws)
        try:
            await self.distrubute(ws)
        except WebSocketProtocolError as err:
            logging.error(err)
        finally:
            await self.unreg(ws)
    
    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message == 'exchange':
                message = await get_exchange()
                await self.send_to_clients(message)
            else:
                await self.send_to_clients(F"{ws.name}: {message}")
    
async def main():
    srv = Server()
    async with websockets.serve(srv.ws_handler, 'localhost', 8080):
        await asyncio.Future()
    
if __name__ == "__main__":
    asyncio.run(main())
