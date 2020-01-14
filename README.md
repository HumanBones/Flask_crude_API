# Flask_crude_API
Crud API made in flask with SQLAlchemy

In this project I used Flask, SQLAlchemy, Marshmallow and JWT.
Instead of vienv I used pipenv, it is much simpler to operate and keeps everything installed in a pipfile.


-This is a simple product schem API with custom json error outputs and simple jwt.

Marshmallow was used for making the schema fields.
It does not have users, jwt is authenticated only by a password witch is ('password'), username can be random.
Also token has an expiration time of 30min.

For debuging and testing I used Postman.
