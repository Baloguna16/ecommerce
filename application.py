import os

from __init__ import create_app

#create app thru app factory pattern
app = create_app()

if __name__ == "__main__":
    app.run(ssl_context="adhoc")
