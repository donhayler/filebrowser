# File Browser REST API

This is a simple file browser REST API I built while learning Python and Flask.
.  It provides GET operations and a swagger doc UI.

In order to run this application, create a named docker volume called
"files_volume" that contains the root directory the application should use.
All files in this directory will be accessible through the application REST
API.  For example:

```
docker volume create --name files_volume --opt type=none --opt device=/Users/dhayler/dev/filebrowser/files --opt o=bind
```

Then, start the application using the `docker-compose up` command.  The
application will then be accessible at http://localhost:9007.

The application can also be started locally using the `python app.py -p ./files`
command where "./files" is the path to the root directory you wish to use.

The code can be tested using the `python -m unittest` command.

The Swagger json is available at http://localhost:9007/api/spec and the
Swagger UI is available at http://localhost:9007/api/docs.

## Notes

To set up a new Python project:

1. create new project directory
1. pip3 install virtualenv
1. virtualenv env
1. source venv/bin/activate
1. pip install <whatever packages you need>

I decided to use Flask instead of Django because it seemed simpler for a basic
REST API.

## References

1. https://pypi.org/project/flask-swagger/
1. https://pypi.org/project/flask-swagger-ui/

I really enjoyed learning Python and some of the ways it is drastically different
from Java, the language I most commonly use.  I was pleasantly surprised at how
well the Flask and swagger packages worked and how easy they were to use.

## Issues

1. Basic GET functionality was implemented, but I did not thoroughly investigate
edge cases around non-regular files, such as block special device files.
1. POST, PUT, and DELETE, also need to be implemented. 
1. This implementation uses the built-in Python webserver, which should be replaced
before this application is deployed to production.
1. This application does not provide any authentication checks.
1. Issues around security and permissions accessing files and directories have
not been investigated.
1. The docker-compose.yml file could be updated to automatically create the named
volume using an environment to specify the host path. 
1. The computer readable Swagger JSON is only tested by checking that it's there and
does not check that is correct or even json.  You would not want to check the
validity of this via unit test.  Note that the Swagger JSON is created by a
comment in the code itself to make it easier to keep the documentation in sync
with the code as compared to having the docs in a separate file. 
1. The Swagger UI was not tested in unit tests because it did not seem to work using
the test client.  Ideally we would test that the Swagger UI is present in unit
tests, although we probably do not want to test it exhaustively.  It might be a
good idea to check for errors in the UI via unit test to catch cases where the
Swagger data in the code is invalid.