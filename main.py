from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, Response
from crypto_api import get_crypto_data
from portfolio_db import get_user_portfolio, add_or_update_asset
from database import db_conn, pwd_context
from portfolio_db import delete_asset

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.post("/signup")
async def registr(username: str = Form(...), password: str = Form(...)):
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Login = ?", (username,))
        if cursor.fetchone():
            return {"status": "error", "message": "Этот логин уже занят!"}

        if username == password:
            return {"status": "error", "message": "Логин не должен совпадать с паролем"}

        hashed_password = pwd_context.hash(password)
        cursor.execute("INSERT INTO Users (Login, Password) VALUES (?, ?)", (username, hashed_password))
        db_conn.commit()
        
        return RedirectResponse(url="/login_page", status_code=303)
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    cursor = db_conn.cursor()
    cursor.execute("SELECT id, Password FROM Users WHERE Login = ?", (username,))
    result = cursor.fetchone()

    if result and pwd_context.verify(password, result["Password"]):
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="user_id", value=str(result["id"]), httponly=True)
        return response
    
    return {"status": "error", "message": "Неверный логин или пароль"}

@app.get("/login_page")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login_page.html")

@app.get("/signup_page")
async def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="signup_page.html")

@app.get("/")
async def home(request: Request):
    user_id = request.cookies.get("user_id")
    if user_id is None:
        return RedirectResponse(url="/login_page", status_code=303)

    portfolio = await get_user_portfolio(int(user_id))
    coin_ids = list(portfolio.keys())

    data = get_crypto_data(coin_ids) if coin_ids else {}

    if data is None:
        data = {}
    else:
        for coin, amount in portfolio.items():
            if coin in data:
                data[coin]['amount'] = amount
                data[coin]['total'] = data[coin].get('rub', 0) * amount
    
    total_balance = 0
    if data:
        for coin, amount in portfolio.items():
            if coin in data:
                data[coin]['amount'] = amount
                coin_total = data[coin].get('rub', 0) * amount
                data[coin]['total'] = coin_total
                total_balance += coin_total
    
    print(f"DEBUG: Coins from DB: {coin_ids}")
    print(f"DEBUG: Data from API: {data}")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"crypto_data": data, "total_balance": total_balance}
    )


@app.get("/add")
async def add_coin_page(request: Request):
    return templates.TemplateResponse(request=request, name="add_coin.html")

@app.post("/add")
async def add_coin_to_portfolio(request: Request, coin_id: str = Form(...), amount: float = Form(...)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login_page", status_code=303)

    await add_or_update_asset(int(user_id), coin_id, amount)
    return RedirectResponse(url="/", status_code=303)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login_page", status_code=303)
    response.delete_cookie("user_id")
    return response

@app.get("/delete/{coin_id}")
async def delete_coin(request: Request, coin_id: str):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login_page", status_code=303)
    
    await delete_asset(int(user_id), coin_id)
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)