// Execute when the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {

	// Hide warnings by default
	document.querySelectorAll(".alert-danger").forEach(div => {

	div.style.visibility = "hidden";
	})
	// JS for the Stocks page
	if (window.location.href == 'http://' + document.domain + ':' + location.port + "/stocks") {
		
		// Send an AJAX request when the user wants to buy shares
		document.querySelector("#buy").onsubmit = event => {

			var my_item = {"shares": document.querySelector("#buy_shares").value,
							"symbol": document.querySelector("#buy_symbol").value};
			myRequest(event, "/buy", my_item);
		}

		// Send an AJAX request when the user wants to sell shares
		document.querySelector("#sell").onsubmit = event => {
			var my_item = {"shares": document.querySelector("#sell_shares").value,
							"symbol": document.querySelector("#sell_symbol").value};
			myRequest(event, "/sell", my_item);
		}

		// Send an AJAX request when the user wants to get price a quote for a stock
		document.querySelector("#quote").onsubmit = event => {
			
			var my_item = {"symbol": document.querySelector("#quote_symbol").value};
			myRequest(event, "/quote", my_item);
		
		}
	}

	// JS for the Register page
	else if (window.location.href == 'http://' + document.domain + ':' + location.port + "/register") {
		
		// Execute when the user submits the register form
		document.querySelector("#register").onsubmit = event => {
			
			// Grab HTML elements that are needed
			var regusername = document.querySelector("#regusername");
			var reg_username = document.querySelector("#reg_username");
			var regpw = document.querySelector("#regpw");
			var reg_pw = document.querySelector("#reg_pw");
			var regconf = document.querySelector("#regconf");
			var reg_confirmation = document.querySelector("#reg_confirmation");

			// Prepare data for the AJAX request
			var my_item = {"username": reg_username.value, "password": reg_pw.value,
							"confirmation": reg_confirmation.value,
							 "starting_balance": document.querySelector("#starting_balance").value};
			
			// Password mismatch
			if (reg_pw.value != reg_confirmation.value) {
				
				// Show appropriate message to guide the user
				threeInputs("two_wrong",regusername, reg_username, regpw, 
					"The password and its confirmation do not match", reg_pw, regconf, reg_confirmation);
				return false;
			}
			// Send AJAX request if all checks are cleared
			myRequest(event, "/register", my_item);
		}	
	}
	// JS for the Change Password page
	else if (window.location.href == 'http://' + document.domain + ':' + location.port + "/change-pw") {
		
		// Execute when the user submits the change password form
		document.querySelector("#change_pw").onsubmit = event => {
			
			// Grab HTML elements that are needed
			var oldpw = document.querySelector("#oldpw");
			var old_pw = document.querySelector("#old_pw");
			var newpw = document.querySelector("#newpw");
			var new_pw = document.querySelector("#new_pw");
			var changeconf = document.querySelector("#changeconf");
			var change_confirmation = document.querySelector("#change_confirmation");

			// Prepare data for the AJAX request
			var my_item = {"old_password": old_pw.value, "new_password": new_pw.value,
						"confirmation": change_confirmation.value};
			
			// New password same as old
			if (old_pw.value == new_pw.value) {

				// Show appropriate message to guide the user
				threeInputs("two_wrong", changeconf, change_confirmation, newpw, "Old and new passwords are the same",
					new_pw, oldpw, old_pw);
				return false;
			
			}

			// Password mismatch
			else if (new_pw.value != change_confirmation.value) {

				// Show appropriate message to guide the user
				threeInputs("two_wrong", oldpw, old_pw, changeconf, "The new password and its confirmation do not match",
					change_confirmation, newpw, new_pw);
				return false;
			}

			// Send an AJAX request if all checks are cleared
			myRequest(event, "/change-pw", my_item);
		}

	}

	// JS for the Login page
	else if (window.location.href == 'http://' + document.domain + ':' + location.port + "/login") {

		// Send an AJAX request when the user submits the login form
		document.querySelector("#login").onsubmit = event => {

			var my_item = {"username": document.querySelector("#login_user").value,
							"password": document.querySelector("#login_pw").value};

			myRequest(event, "/login", my_item);
		}
	}
	// JS for the history page
	else if (window.location.href == 'http://' + document.domain + ':' + location.port + "/history") {

		// Delete the selected item from the financial history
		deleteItem(".delete_hist", "delete_hist_id", "/delete_hist");

		// Show the edit form for the selected item from the financial history
		editItem(".edit_hist", "#edit_hist", "#edit_hist_id");

		// Edit the selected entry when the user submits the edit entry form
		document.querySelector("#edit_hist").onsubmit = event => {

			var my_item = {"edit_hist_id": document.querySelector("#edit_hist_id").value, 
			"edit_hist_type": document.querySelector("#edit_hist_type").value, 
			"edit_hist_title": document.querySelector("#edit_hist_title").value,
			"edit_hist_amount": document.querySelector("#edit_hist_amount").value};

			myRequest(event, "/edit_hist", my_item);
		}

		// Disable the delete all button if the financial history is empty
		emptyTable(".delete_hist", "#delete_all_hist");

		// Execute when the user clicks on the delete all button
		document.querySelector("#delete_all_hist").onclick = event => {

			// Ask the user to confirm their intentions
			var c = confirm("You are about to delete the financial history, the stock portfolio " +
				"and the transaction history of your account. Your account will be emptied, and its "+
				"starting balance will be reset to 10,000.00 USD." +
				" Do you wish to proceed?");

			/* Empty the user's financial history, stock portfolio and their transaction history,
			then reset their starting balance to 10K USD */
			if (c == true) {
				var my_item = {"delete_all_check2": "check"};

				myRequest(event, "/delete_all_hist", my_item);
			}
		}

		/* Show the edit starting balance form when the user clicks on the "Change starting balance" button
		 and hide the button itself*/
		document.querySelector("#editbalance").onclick = () => {

			document.querySelector("#edit_balance").style.display = "block";
			document.querySelector("#editbalance").style.display = "none";
		}
		
		/* Hide the transaction history table when the user clicks on the "Hide transaction history" button
		 Hide the button itself and show the "Show transaction history" button instead*/
		document.querySelector("#hidetransactions").onclick = () => {

			document.querySelector("#showtransactions").style.display = "inline";
			document.querySelector("#transactions").style.display = "none";
			document.querySelector("#hidetransactions").style.display = "none";
		}

		/* Show the transaction history table and the "Hide transaction history" button 
		 when the user clicks on the "Show transaction history" button and hide the button itself*/
		document.querySelector("#showtransactions").onclick = () => {

			document.querySelector("#showtransactions").style.display = "none";
			document.querySelector("#transactions").style.display = "table";
			document.querySelector("#hidetransactions").style.display = "inline";
		}
	}
	// JS for the main page
	else {
		
		// Delete the selected item from the recurring entries table
		deleteItem(".delete_auto", "delete_id", "/delete_auto");

		// Show the edit recurring entry form for the selected entry
		editItem(".edit_auto", "#edit_auto", "#edit_id");

		// Edit the selected entry when the user submits the edit recurring entry form
		document.querySelector("#edit_auto").onsubmit = event => {

			var my_item = {"edit_id": document.querySelector("#edit_id").value, 
			"edit_type": document.querySelector("#edit_type").value, 
			"edit_title": document.querySelector("#edit_title").value,
			"edit_amount": document.querySelector("#edit_amount").value,
			"edit_frequency": document.querySelector("#edit_frequency").value};

			myRequest(event, "/edit_auto", my_item);
		}
		
		// Disable the delete all button if the recurring entries table is empty
		emptyTable(".delete_auto", "#delete_all_auto");

		// Execute when the user clicks on the delete all button
		document.querySelector("#delete_all_auto").onclick = event => {

			// Ask the user to confirm their intentions
			var c = confirm("You are about to delete all recurring entries that belong to your account." +
				" Do you wish to proceed?");

			// Empty the recurring entries table after receiving confirmation
			if (c == true) {
				var my_item = {"delete_all_check": "check"};

				myRequest(event, "/delete_all_auto", my_item);
			}
		}
	}

});

function invalidInput(div_to_hide, right_part, div_to_show, error_message, wrong_part) {
/* Help users find the issue with their input using messages and CSS */

	div_to_hide.style.visibility = "hidden";
	right_part.style.border = "1px solid #ced4da";
	div_to_show.innerHTML = error_message;
	div_to_show.style.visibility = "visible";
	wrong_part.style.border = "1px solid red";
	wrong_part.focus();
}

function threeInputs(state, div_to_hide, right_part, div_to_show, error_message, wrong_part, third_div, third_part) {
/* Similiar to the invalidInput function, but tailored for forms with three possible sources of error */
	div_to_hide.style.visibility = "hidden";
	right_part.style.border = "1px solid #ced4da";
	div_to_show.innerHTML = error_message;
	div_to_show.style.visibility = "visible";
	wrong_part.style.border = "1px solid red";
	third_div.style.visibility = "hidden";
	wrong_part.focus();

	/* Either the user has two right inputs or two wrong ones. The third form element is styled depending on 
	 which one is the case. */
	if (state == "two_right") {

		third_part.style.border = "1px solid #ced4da";
	}
	else {

		third_part.style.border = "1px solid red";
	}

}

function myRequest(event, url, items) {
/* Sends an AJAX request to specific URLs with data that was organized prior to sending the request */
	
	// Create and open the request
	const request = new XMLHttpRequest();
	request.open("POST", url);

	// Do something after receiving the server's response
	request.onload = () => {

		// Parse the response
		if (request.responseText[0] == "{") {
			 var my_data = JSON.parse(request.responseText);
		}
		else {
			 var my_data = {"error": "nope"};
		}

		// React differently depending on which URL is involved
		if (url == "/buy") {
			
			buyOnLoad(my_data);
		}
		else if (url == "/sell") {

			sellOnLoad(my_data);
		}
		else if (url == "/quote") {

			quoteOnLoad(my_data);
		}
		else if (url == "/register") {

			registerOnLoad(my_data);
		}
		else if( url == "/change-pw") {
			changeOnLoad(my_data);
		}
		else if (url == "/login") {
			loginOnLoad(my_data);
		}
		else {
			location.reload();
		}
	}

	// Send the data that was passed in to the server
	const data = new FormData();

	for (var key in items) {

		data.append(key, items[key]);
	}

	request.send(data);

	// Prevent default mechanisms like form submission
	event.preventDefault();
}

function buyOnLoad(data) {
	/* Handle the server's response to submitting the buy shares form */

	// grab HTML elements that are needed
	var buysymbol = document.querySelector("#buysymbol");
	var buyshares = document.querySelector("#buyshares");
	var buy_symbol = document.querySelector("#buy_symbol");
	var buy_shares = document.querySelector("#buy_shares");

	// Notify the user that the stock symbol they entered is invalid
	if (data["error"] == "1") {

		invalidInput(buyshares, buy_shares, 
			buysymbol, "Invalid stock symbol", buy_symbol);
	
	}

	// Notify the user that they can't afford the transaction they decided on
	else if(data["error"] == "2") {

		invalidInput(buysymbol, buy_symbol, 
			buyshares, "Insufficient funds", buy_shares);
	}

	// Reload the page if the transaction was successful
	else {

		location.reload();
	}

}

function sellOnLoad(data) {
/* Handle the server's response to submitting the sell shares form */
	
	// Grab the HTML elements that are needed
	var sellsymbol = document.querySelector("#sellsymbol");
	var sell_symbol = document.querySelector("#sell_symbol");
	var sellshares = document.querySelector("#sellshares");
	var sell_shares = document.querySelector("#sell_shares");

	// Wrong stock
	if (data["error"] == "1") {

		invalidInput(sellshares, sell_shares, sellsymbol, 
			"You don't have the selected stock in your portfolio", sell_symbol);
	}

	// No shares of the selected stock
	else if (data["error"] == "2") {

		invalidInput(sellshares, sell_shares, sellsymbol, 
			"You don't own any shares of this stock", sell_symbol);
	}

	// Not enough shares for the transaction
	else if (data["error"] == "3") {

		invalidInput(sellsymbol, sell_symbol, sellshares, 
			"You don't own enough shares for this transaction", sell_shares);
	}

	// Success
	else {

		location.reload();

	}
}

function quoteOnLoad(data) {
/* Handle the server's response to submitting the quote form*/

	// Grab the HTML elements that are needed
	var quotesymbol = document.querySelector("#quotesymbol");
	var quote_symbol = document.querySelector("#quote_symbol");

	// Invalid stock symbol
	if (data["error"]) {

		quotesymbol.style.visibility = "visible";
		quote_symbol.style.border = "1px solid red";
		quotesymbol.innerHTML = "Invalid stock symbol";
		quote_symbol.focus();
	}
	
	// Success
	else {

		// Show an alert with the info the user requested
		quotesymbol.style.visibility = "hidden";
		quote_symbol.style.border = "1px solid #ced4da";
		alert("The price of a " + String(data["symbol"]) + " stock is " + String(data["price"] + " USD."));
	}
}

function registerOnLoad(data) {
/* Handle the server's response to submitting the register form */

	// Grab the HTML elements that are needed
	var regusername = document.querySelector("#regusername");
	var reg_username = document.querySelector("#reg_username");
	var regpw = document.querySelector("#regpw");
	var reg_pw = document.querySelector("#reg_pw");
	var regconf = document.querySelector("#regconf");
	var reg_confirmation = document.querySelector("#reg_confirmation");
	
	// Username taken
	if (data["error"] == "1") {

		threeInputs("two_right", regpw, reg_pw, regusername, "Username already taken",
			reg_username, regconf, reg_confirmation);
	}

	// Success
	else {

		// Redirect user to the main page
		window.location.href = "/";
	}

}

function changeOnLoad(data) {
/* Handle the server's response to submitting the change password form*/
	
	// Grab the HTML elements that are needed
	var oldpw = document.querySelector("#oldpw");
	var old_pw = document.querySelector("#old_pw");
	var newpw = document.querySelector("#newpw");
	var new_pw = document.querySelector("#new_pw");
	var changeconf = document.querySelector("#changeconf");
	var change_confirmation = document.querySelector("#change_confirmation");

	// Old password does not match records
	if (data["error"] == "1") {

		threeInputs("two_right", newpw, new_pw, oldpw, "Old password does not match records",
			old_pw, changeconf, change_confirmation);
	}

	// Success
	else {

		// Redirect user to the main page
		window.location.href = "/"
	}
}

function loginOnLoad(data) {
/* Handle the server's response to submitting the login form */

	// Invalid credentials
	if (data["error"] == "1") {

		document.querySelector("#loginpw").style.visibility = "hidden";
		document.querySelector("#login_pw").style.border = "1px solid red";
		document.querySelector("#loginuser").style.visibility = "visible";
		document.querySelector("#loginuser").innerHTML = "Invalid username or password";
		document.querySelector("#login_user").style.border = "1px solid red";
		document.querySelector("#login_user").focus();
	}

	// Success
	else {

		// Redirect user to the main page
		window.location.href = "/"
	}
}

function deleteItem(my_class, my_key, my_url) {
/* Sends an AJAX request to delete the specified item from the specified table */

	// Execute when a delete button from the specified class is clicked
	document.querySelectorAll(my_class).forEach(button => {

			// Send the AJAX request
			button.onclick = event => {
				
				var my_item = {[my_key]: button.dataset.my_id};
				myRequest(event, my_url, my_item);

			}
		});
}

function editItem(my_class, my_form, my_div) {
/* Shows the specified edit form for the specified element in the specified table*/

	document.querySelectorAll(my_class).forEach(button => {
			button.onclick = () => {

				document.querySelector(my_form).style.display = "block";
				document.querySelector(my_div).value = button.dataset.my_id;
				document.querySelector(my_div).innerHTML = `Entry ID: <strong>${button.dataset.my_id}</strong>`;
			}
		});
}

function emptyTable(my_class, my_button) {
/* Checks if the specified table is empty, disables/enables the delete all button accordingly*/

	if (document.querySelectorAll(my_class).length == 0) {

		document.querySelector(my_button).disabled = true;
	}
	else {

		document.querySelector(my_button).disabled = false;
	}
}