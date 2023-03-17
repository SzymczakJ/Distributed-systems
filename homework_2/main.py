import asyncio
import json

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from fastapi.templating import Jinja2Templates
import aiohttp

from pydantic import BaseModel

app = FastAPI()

geo_api_key = "5c3a8f42e0bb5701e28fe8f850550393"

@app.get("/")
async def get_form():
    with open("Form.html") as html_file:
        return HTMLResponse("".join(html_file.readlines()))


async def fetch(url, session):
    async with session.get(url) as response:
        return await response.read()


@app.post("/", response_class=HTMLResponse)
async def get_weather(request: Request, pokemon: str = Form()):
    tasks = []
    async with aiohttp.ClientSession() as session:
        urls = ["https://pokeapi.co/api/v2/pokemon/" + pokemon, "https://pokeapi.co/api/v2/pokemon/pikachu"]
        for url in urls:
            task = asyncio.ensure_future(fetch(url, session))
            tasks.append(task)

        templates = Jinja2Templates(directory="templates")
        try:
            responses = await asyncio.gather(*tasks)
            pokemon = json.loads(responses[0])
            pikachu = json.loads(responses[1])
            context = {
                "request": request,
                "pokemon_name": pokemon["name"],
                "height_difference": pikachu["height"] - pokemon["height"],
                "weight_difference": pikachu["weight"] - pokemon["weight"]
            }
            return templates.TemplateResponse("ResultsSuccessful.html", context)
        except Exception as e:
            print(e)
            with open("ResultsFailure.html") as html_file:
                return HTMLResponse("".join(html_file.readlines()))
