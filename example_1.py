'''
이 파일은 FastAPI를 사용하여 간단한 웹 API 서버를 구현한 예제입니다.
기본 경로('/')와 아이템 정보를 조회하는 경로('/items/{item_id}')를 제공합니다.
'''
from typing import Union
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

# FastAPI 애플리케이션 인스턴스 생성 
app = FastAPI()

# 아이템 모델 
class Item(BaseModel) : 
        name : str 
        price : float 
        is_offer : Union[bool , None ] = None

# 루트 경로 
@app.get('/')
def read_root( ):
    return "if you want to see the items, go to :/items/1?q=my_query"

# 아이템 조회 
@app.get("/items/{item_id}") 
def read_item(item_id : int, q : Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# 아이템 업데이트 
@app.put("/items/{item_id}")
def update_item(item_id : int, item : Item) : 
     return {"item_name" : item.name , "item_id" : item_id} 

