from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

# command for run the server
#  uvicorn main:app --host localhost --port 8000 --reload
app = FastAPI(title="FastAPI CRUD - Single File Example")

# מודלים
class Item(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None

# data
items_db: List[Item] = [
    Item(id=1, name="Laptop", price=3000, description="Gaming laptop"),
    Item(id=2, name="Phone", price=2000, description="Smartphone"),
]

# ROUTES
#  curl http://localhost:8000
@app.get("/")
def root():
    return {"message": "Welcome to FastAPI CRUD (single-file) !"}

# curl -X POST "http://localhost:8000/items/" -H "Content-Type: application/json" -d '{"id":3,"name":"Tablet","price":1500,"description":"Android tablet"}'
@app.post("/items/", response_model=Item, status_code=201)
def create_item(item: Item):
    # # בדיקה שאין כפילות ID
    if any(it.id == item.id for it in items_db):
        raise HTTPException(status_code=400, detail="Item with this id already exists")
    items_db.append(item)
    return {item}

# curl "http://localhost:8000/items/"
# READ (All) - קבלת כל הפריטים (ללא פרמטרים)
@app.get("/items/", response_model=List[Item])
def get_all_items():
    return items_db

# curl "http://localhost:8000/items/2"
# READ (One) - קבלת פריט לפי מזהה (Path Param)
@app.get("/items/{item_id}", response_model=Item)
def get_item_by_id(item_id: int):
    for it in items_db:
        if it.id == item_id:
            return it
    raise HTTPException(status_code=404, detail="Item not found")

# READ (Search) - חיפוש עם Query Param (לא חובה)
# דוגמה: /items/search?q=phone
@app.get("/items/search")
def search_items(q: Optional[str] = None, limit: Optional[int] = None):
    results = items_db
    if q:
        results = [it for it in results if q.lower() in it.name.lower()]
    if limit is not None:
        results = results[:max(0, limit)]
    return {"query": q, "count": len(results), "results": results}

# curl -X PUT "http://localhost:8000/items/2" -H "Content-Type: application/json" -d "{\"id\":2,\"name\":\"Phone Pro\",\"price\":2200,\"description\":\"Updated smartphone\"}"
# PUT (Body + Path Param)
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, new_item: Item):
    """
מצפה לכל האובייקט item
מקבל את הid בפארמס    """
    for idx, it in enumerate(items_db):
        if it.id == item_id:
            items_db[idx] = new_item
            return new_item
    raise HTTPException(status_code=404, detail="Item not found")

# curl -X DELETE "http://localhost:8000/items/2"
# DELETE
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    for idx, it in enumerate(items_db):
        if it.id == item_id:
            deleted = items_db.pop(idx)
            return {"deleted": deleted}
    raise HTTPException(status_code=404, detail="Item not found")
