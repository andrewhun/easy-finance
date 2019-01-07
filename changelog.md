# Changelog for Easy Finance v2.0

I've managed to expand and change the program quite a bit. The main changes compared to v1.2 are as follows:

- Replaced the Flask-SQLAlchemy backend with Django
- Added unit tests and functional tests (137 tests altogether) to the application
- Added configuration files for Travis CI and Docker (not sure if the Docker one works)
- Updated the documentation to better fit the current state of the app (shaved off some 10 pages of needless stuff, too)
- Completed the "add recurring entries" feature

Regarding the last point, I have to admit that the result is quite shabby. 
I am relying on a module called django-background-tasks. It does the job, but it has a few quirks:
- You need to set up the system before it is ready. You have to open a second terminal window,
navigate to the project folder and run "python manage.py process_tasks" before starting the server.
If you neglect doing so the scheduled tasks simply won't be carried out.
- When you schedule a task, it is executed once immediately. This may or may not be what the user wants.
In any case, the ambiguity is an issue.

I've found two useful sources of information on django-background-tasks:
- The documentation: https://django-background-tasks.readthedocs.io/en/latest/
- A handy tutorial: https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e

I spent a long time writing the tests. Harry Percival's book (which you can read for free on 
https://www.obeythetestinggoat.com/) was a huge help. If you could use some guidance on testing
Django apps, this book is a good choice.
