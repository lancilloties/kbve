from fastapi import FastAPI, WebSocket,  HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles


import uvicorn

from contextlib import asynccontextmanager

from kbve_atlas.api.clients import CoinDeskClient, WebsocketEchoClient, PoetryDBClient, ScreenClient, NoVNCClient
from kbve_atlas.api.utils import RSSUtility, KRDecorator, CORSUtil, ThemeCore, BroadcastUtility

import logging
logger = logging.getLogger("uvicorn")


# TODO : broadcast = ENV_REDIS_FILE For k8s/swarm.
broadcast = BroadcastUtility()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[BROADCAST]@PENDING")
    await broadcast.connect()
    yield
    logger.info("[BROADCAST]@DISINT")
    await broadcast.disconnect()


app = FastAPI(lifespan=lifespan)

kr_decorator = KRDecorator(app)

CORSUtil(app)

novnc_client = NoVNCClient()
app.include_router(novnc_client.router)

app.mount("/novnc", StaticFiles(directory="/app/templates/novnc", html=True), name="novnc")

@app.websocket("/websockify")
async def websocket_default_proxy(websocket: WebSocket):
    await novnc_client.ws_vnc_proxy(websocket, "localhost", 6080)

@app.websocket("/")
async def chatroom_ws(websocket: WebSocket):
    await websocket.accept()
    await broadcast.send_messages(websocket, "chatroom")

@app.get("/", response_class=HTMLResponse)
async def get():
    return ThemeCore.example_chat_page()

@app.get("/click")
async def click_main():
    # TODO Opps, need to replace this with the right image to click test.
    image_url = "http://example.com/path/to/image.png"
    client = ScreenClient(image_url, timeout=3)
    await client.find_and_click_image()

@app.get("/echo")
async def echo_main():
    websocket_client = WebsocketEchoClient()
    try:
        await websocket_client.example()
    finally:
        await websocket_client.close()
        return {"ws": "true"}


@app.get("/news")
async def google_news():
    rss_utility = RSSUtility(base_url="https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en")
    try:
        soup = await rss_utility.fetch_and_parse_rss()
        rss_feed_model = await rss_utility.convert_to_model(soup)
        formatted_feed = RSSUtility.format_rss_feed(rss_feed_model)
        return {"news": formatted_feed}
    except:
        return {"news": "failed"}

@kr_decorator.k_r("/bitcoin-price", CoinDeskClient, "get_current_bitcoin_price")
def bitcoin_price(price):
    return {"bitcoin_price": price}

@kr_decorator.k_r("/poem", PoetryDBClient, "get_random_poem")
def poetry_db(poem):
    return {"poem": poem}
