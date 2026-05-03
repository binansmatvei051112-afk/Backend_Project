from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from crypto_api import get_crypto_data

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

user_portfolio = {
    "bitcoin": 0.05,
    "ethereum": 0.5,
    "solana": 10.0,
    "dogecoin": 1000.0
}

@app.get("/")
async def home(request: Request):
    data = get_crypto_data(list(user_portfolio.keys()))
    
    if data is None:
        data = {}
    else:
        for coin, amount in user_portfolio.items():
            if coin in data:
                data[coin]['amount'] = amount
                data[coin]['total'] = data[coin].get('rub', 0) * amount

    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"crypto_data": data}
    )

@app.get("/add")
async def add_coin_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="add_coin.html"
    )

@app.post("/add")
async def add_coin_to_portfolio(coin_id: str = Form(...), amount: float = Form(...)):
    user_portfolio[coin_id] = amount
    
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)