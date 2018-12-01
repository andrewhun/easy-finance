Easy Finance v.1.2

Changes compared to v1.1:

- Replaced JQuery with ES6
- An attempt was made to improve the overall design of the JavaScript module (this basically means the (over)use of functions wherever applicable)
- The way users can edit and delete table elements was improved. Added Edit and Delete buttons to each of the elements and placed the delete all buttons at the bottom of both tables (financial history, recurring entries)
- Got rid of some of the now redundant elements, such as the delete entry forms and a few buttons
- The user is now asked to confirm their decision to empty tables via JavaScript's confirm() method.

Easy Finance v1.1

Changes compared to the original version:
- The database operations now use SQLAlchemy instead of CS50's SQL module
- The program now uses a database hosted on Heroku (Postgres) instead of a local database file
- Much of the input validation is now done on the client's side (in JavaScript and using HTML's "required" attribute)
- The "delete all recurring entries" and "delete all entries" functions were separated from the "delete recurring entry" and "delete entry" functions
- The appearance of the program is different, mostly due to changes in the coloring

In general I intended to optimize how the program works. I also wanted to minimize its reliance on tools that were supplied by the CS50 staff, in order to make it more of a "real" app.
