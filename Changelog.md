Easy Finance v1.1

Changes compared to the original version:
- The database operations now use SQLAlchemy instead of CS50's SQL module
- The program now uses a database hosted on Heroku (Postgres) instead of a local database file
- Much of the input validation is now done on the client's side (in JavaScript and using HTML's "required" attribute)
- The "delete all recurring entries" and "delete all entries" functions were separated from the "delete recurring entry" and "delete entry" functions
- The appearance of the program is different, mostly due to changes in the coloring

In general I intended to optimize how the program works. I also wanted to minimize its reliance on tools that were supplied by the CS50 staff, in order to make it more of a "real" app.
