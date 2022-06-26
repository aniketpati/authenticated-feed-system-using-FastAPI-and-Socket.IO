from fastapi import FastAPI

SECRET = 'your-secret-key'

app = FastAPI()
from fastapi_login import LoginManager

manager = LoginManager(SECRET, token_url='/auth/token')
fake_db = {'johndoe@e.mail': {'password': 'hunter2'}}

@manager.user_loader()
def load_user(email: str):  # could also be an asynchronous function
    user = fake_db.get(email)
    return user

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException

# the python-multipart package is required to use the OAuth2PasswordRequestForm
@app.post('/auth/token')
def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = load_user(email)  # we are using the same function to retrieve the user
    if not user:
        raise InvalidCredentialsException  # you can also use your own HTTPException
    elif password != user['password']:
        raise InvalidCredentialsException
    
    access_token = manager.create_access_token(
        data=dict(sub=email)
    )
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.get('/protected')
def protected_route(user=Depends(manager)):
    ...

from starlette.responses import RedirectResponse

class NotAuthenticatedException(Exception):
    pass

# these two argument are mandatory
def exc_handler(request, exc):
    return RedirectResponse(url='/login')

# This will be deprecated in the future
# set your exception when initiating the instance
# manager = LoginManager(..., custom_exception=NotAuthenticatedException)
manager.not_authenticated_exception = NotAuthenticatedException
# You also have to add an exception handler to your app instance
app.add_exception_handler(NotAuthenticatedException, exc_handler)


from datetime import timedelta

data = dict(sub=user.email)

# expires after 15 min
token = manager.create_access_token(
    data=data
)
# expires after 12 hours
long_token = manager.create_access_token(
    data=data, expires=timedelta(hours=12)
)

from fastapi_login import LoginManager

manager = LoginManager(SECRET, token_url='/auth/token', use_cookie=True)

from fastapi import Depends
from starlette.responses import Response


@app.get('/auth')
def auth(response: Response, user=Depends(manager)):
    token = manager.create_access_token(
        data=dict(sub=user.email)
    )
    manager.set_cookie(response, token)
    return response
    