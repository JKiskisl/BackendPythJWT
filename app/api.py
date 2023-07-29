
from fastapi import FastAPI, Body, Depends, HTTPException, status

from app.model import PostSchema, UserSchema, UserLoginSchema, UpdatePostSchema
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from passlib.context import CryptContext
from app.auth.auth_handler import decodeJWT

from fastapi.responses import JSONResponse
from app.custom_json_encoder import CustomJSONEncoder
import json
from bson.json_util import dumps

client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
users_collection = db["users"]
posts_collection = db["posts"]

users_collection.create_index("email", unique=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



app = FastAPI()


async def get_current_user(token: str = Depends(JWTBearer())):
    payload = decodeJWT(token)
    email = payload.get("user_id")
    user_data = users_collection.find_one({"email": email})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user_data


async def get_current_email(token: str = Depends(JWTBearer())):
    payload = decodeJWT(token)
    email = payload.get("user_id")
    user_data = users_collection.find_one({"email": email})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    print("User email:", email)
    print (user_data)
    return user_data["email"]



@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your backend!"}


@app.get("/posts", dependencies=[Depends(JWTBearer())], tags=["posts"])
async def get_user_posts(email: str = Depends(get_current_email)) -> dict:
    print(email)
    user_posts = posts_collection.find({"email.email": email})
    serialized_posts = dumps(list(user_posts), cls=CustomJSONEncoder)
    return JSONResponse(content={"data": json.loads(serialized_posts)})


@app.get("/posts/{id}", dependencies=[Depends(JWTBearer())], tags=["posts"])
async def get_single_post(id: int, email: str = Depends(get_current_email)) -> dict:
    post_data = posts_collection.find_one({"id": id, "email.email": email})
    serialized_post = dumps((post_data), cls=CustomJSONEncoder)
    if serialized_post:
        return JSONResponse(content={"data": json.loads(serialized_post)})
    return {
        "error":"No such post with supplied ID."
    }
            
@app.post("/posts", dependencies=[Depends(JWTBearer())], tags=["posts"])
async def add_post(post: PostSchema, email=Depends(get_current_user)) -> dict:
    post_data = post.dict()
    post_data["email"] = email
    post_data["id"] = posts_collection.count_documents({}) + 1
    posts_collection.insert_one(post_data)
    return {
        "data": "post added."
    }
    
    
@app.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    hashed_password = pwd_context.hash(user.password)
    try:
        user_data = user.dict()
        user_data["password"] = hashed_password
        users_collection.insert_one(user_data)
        return signJWT(user.email)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already in use")


def check_user(data: UserLoginSchema):
    user_data = users_collection.find_one({"email": data.email})
    if user_data and pwd_context.verify(data.password, user_data["password"]):
        return True
    return False

@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    return {
        "error": "Wrong login details!"
    }
    
    

@app.delete("/posts/{id}", dependencies=[Depends(JWTBearer())], tags=["posts"])
async def delete_post(id: int, email: str = Depends(get_current_email)) -> dict:
    existing_post = posts_collection.find_one({"id": id, "email.email": email})
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")
    posts_collection.delete_one({"id": id, "email.email": email})
    return {"data": "Post deleted succesfully"}


@app.put("/posts/{id}", dependencies=[Depends(JWTBearer())], tags=["posts"])
async def update_post(id: int, post: UpdatePostSchema, email: str = Depends(get_current_email)) -> dict:
    existing_post = posts_collection.find_one({"id": id, "email.email": email})
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    update_data = post.dict(exclude_unset=True)
    posts_collection.update_one({"id": id, "email.email": email}, {"$set": update_data})
    
    updated_post = posts_collection.find_one({"id": id, "email.email": email})
    serialized_post = dumps(updated_post, cls=CustomJSONEncoder)
    
    return JSONResponse(content={"data": json.loads(serialized_post)})