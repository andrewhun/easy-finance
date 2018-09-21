// Execute when the DOM is fully loaded
$(document).ready(function() {
    // Execute when the buy form is submitted
    $("#buy").on('submit', function(event) {
        // Create a custom AJAX request
        $.ajax({
            data : {
                shares: $("#buy_shares").val(),
                symbol: $("#buy_symbol").val()
            },
            type: "POST",
            url: "/buy"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            // missing stock symbol branch
            if (data.error == "1"){
                $("#buyshares").hide();
                $("#buysymbol").hide();
                $("#buy_symbol").css({"border": "1px solid red"}).show();
                $("#buy_shares").css({"border": "1px solid grey"});
                $("#buysymbol").text("missing stock symbol").show();
                $("#buy_symbol").focus();
            }
            // missing number of shares branch
            else if (data.error == "2"){
                $("#buy_shares").css({"border": "1px solid red"});
                $("#buy_symbol").css({"border": "1px solid grey"});
                $("#buysymbol").hide();
                $("#buyshares").hide();
                $("#buyshares").text("missing number of shares").show();
                $("#buy_shares").focus();
            }
            // invalid number of shares branch
            else if (data.error == "3"){
                $("#buy_shares").css({"border": "1px solid red"});
                $("#buy_symbol").css({"border": "1px solid grey"});
                $("#buysymbol").hide();
                $("#buyshares").hide();
                $("#buyshares").text("invalid number of shares").show();
                $("#buy_shares").focus();
            }
            // invalid stock symbol branch (the Yahoo Finance API couldn't find the stock)
            else if (data.error == "4"){
                $("#buysymbol").hide();
                $("#buyshares").hide();
                $("#buy_shares").css({"border": "1px solid grey"});
                $("#buysymbol").text("Invalid stock symbol").show();
                $("#buy_symbol").css({"border": "1px solid red"});
                $("#buy_symbol").focus();
            }
            // insufficient funds branch
            else if (data.error == "5"){
                $("#buysymbol").hide();
                $("#buyshares").hide();
                $("#buyshares").text("Insufficient funds").show();
                $("#buy_symbol").css({"border": "1px solid grey"});
                $("#buy_shares").css({"border": "1px solid red"});
                $("#buy_shares").focus();
            }
            // success
            else {
                location.reload();
            }
        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // Execute when the sell form is submitted
    $("#sell").on("submit", function(event) {
       // Create a custom AJAX request
        $.ajax({
            data : {
                shares: $("#sell_shares").val(),
                symbol: $("#sell_symbol").val()
            },
            type: "POST",
            url: "/sell"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            // no stock selected branch
            if (data.error == "1") {
                $("#sellshares").hide();
                $("#sellsymbol").hide();
                $("#sell_shares").css({"border": "1px solid grey"}).show();
                $("#sell_symbol").css({"border": "1px solid red"}).show();
                $("#sellsymbol").text("no stock selected").show();
                $("#sell_symbol").focus();
            }
            // missing number of shares branch
            else if (data.error == "2") {
                $("#sellshares").hide();
                $("#sellsymbol").hide();
                $("#sell_symbol").css({"border": "1px solid grey"}).show();
                $("#sell_shares").css({"border": "1px solid red"}).show();
                $("#sellshares").text("missing number of shares").show();
                $("#sell_shares").focus();
            }
            // invalid number of shares branch (less than 1)
            else if (data.error == "3") {
                $("#sellshares").hide();
                $("#sellsymbol").hide();
                $("#sell_symbol").css({"border": "1px solid grey"}).show();
                $("#sell_shares").css({"border": "1px solid red"}).show();
                $("#sellshares").text("invalid number of shares").show();
                $("#sell_shares").focus();
            }
            // stock is not in the portfolio branch (redundant)
            else if (data.error == "4") {
                $("#sellshares").hide();
                $("#sellsymbol").hide();
                $("#sell_shares").css({"border": "1px solid grey"}).show();
                $("#sell_symbol").css({"border": "1px solid red"}).show();
                $("#sellsymbol").text("you don't have the selected stock in your portfolio").show();
                $("#sell_symbol").focus();
            }
            // no shares owned branch
            else if (data.error == "5") {
                $("#sellshares").hide();
                $("#sellsymbol").hide();
                $("#sell_shares").css({"border": "1px solid grey"}).show();
                $("#sell_symbol").css({"border": "1px solid red"}).show();
                $("#sellsymbol").text("you don't own any shares of this stock").show();
                $("#sell_symbol").focus();
            }
            // not enough shares owned branch
            else if (data.error == "6") {
                $("#sellshares").hide();
                $("#sellsymbol").hide();
                $("#sell_symbol").css({"border": "1px solid grey"}).show();
                $("#sell_shares").css({"border": "1px solid red"}).show();
                $("#sellshares").text("you don't own enough shares for this transaction").show();
                $("#sell_shares").focus();
            }
            // success
            else {
                location.reload();
            }
        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // Execute when the change password form is submitted
    $("#change_pw").on("submit", function(event) {
        // Create a custom AJAX request
        $.ajax({
            data : {
                old_password: $("#old_pw").val(),
                new_password: $("#new_pw").val(),
                confirmation: $("#change_confirmation").val()
            },
            type: "POST",
            url: "/change-pw"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            // missing old pw branch
            if (data.error == "1") {
                $("#newpw").hide();
                $("#changeconf").hide();
                $("#oldpw").text("missing old password").show();
                $("#old_pw").css({"border": "1px solid red"});
                $("#new_pw").css({"border": "1px solid grey"});
                $("#change_confirmation").css({"border": "1px solid grey"});
                $("#old_pw").focus();
            }
            // missing new pw branch
            else if (data.error == "2") {
                $("#oldpw").hide();
                $("#changeconf").hide();
                $("#newpw").text("missing new password").show();
                $("#old_pw").css({"border": "1px solid grey"});
                $("#new_pw").css({"border": "1px solid red"});
                $("#change_confirmation").css({"border": "1px solid grey"});
                $("#new_pw").focus()
            }
            // missing confirmation branch
            else if (data.error == "3") {
                $("#newpw").hide();
                $("#oldpw").hide();
                $("#changeconf").text("missing password confirmation").show();
                $("#old_pw").css({"border": "1px solid grey"});
                $("#new_pw").css({"border": "1px solid grey"});
                $("#change_confirmation").css({"border": "1px solid red"});
                $("#change_confirmation").focus()

            }
            // old and new pw are the same branch
            else if (data.error == "4") {
                $("#oldpw").hide();
                $("#changeconf").hide();
                $("#newpw").text("old and new passwords are the same").show();
                $("#old_pw").css({"border": "1px solid red"});
                $("#new_pw").css({"border": "1px solid red"});
                $("#change_confirmation").css({"border": "1px solid grey"});
                $("#old_pw").focus()
            }
            // password mismatch branch
            else if (data.error == "5") {
                $("#newpw").hide();
                $("#oldpw").hide();
                $("#changeconf").text("new password and its confirmation do not match").show();
                $("#old_pw").css({"border": "1px solid grey"});
                $("#new_pw").css({"border": "1px solid red"});
                $("#change_confirmation").css({"border": "1px solid red"});
                $("#new_pw").focus()
            }
            // old pw wrong branch
            else if (data.error == "6") {
                $("#newpw").hide();
                $("#changeconf").hide();
                $("#oldpw").text("old password does not match records").show();
                $("#old_pw").css({"border": "1px solid red"});
                $("#new_pw").css({"border": "1px solid grey"});
                $("#change_confirmation").css({"border": "1px solid grey"});
                $("#old_pw").focus()
            }
            // success
            else {
                // redirect to the main page
                window.location.href = "/";
            }
        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // Execute when the register form is submitted
    $("#register").on("submit", function(event) {
        // Create a custom AJAX request
        $.ajax({
            data : {
                username: $("#reg_username").val(),
                password: $("#reg_pw").val(),
                confirmation: $("#reg_confirmation").val(),
                starting_balance: $("#starting_balance").val()
            },
            type: "POST",
            url: "/register"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            // missing username branch
            if (data.error == "1") {
                $("#regpw").hide();
                $("#regconf").hide();
                $("#regusername").text("missing username").show();
                $("#reg_username").css({"border": "1px solid red"});
                $("#reg_pw").css({"border": "1px solid grey"});
                $("#reg_confirmation").css({"border": "1px solid grey"});
                $("#reg_username").focus();
            }
            // missing password branch
            else if (data.error == "2") {
                $("#regusername").hide();
                $("#regconf").hide();
                $("#regpw").text("missing password").show();
                $("#reg_pw").css({"border": "1px solid red"});
                $("#reg_username").css({"border": "1px solid grey"});
                $("#reg_confirmation").css({"border": "1px solid grey"});
                $("#reg_pw").focus();
            }
            // missing confirmation branch
            else if (data.error == "3") {
                $("#regpw").hide();
                $("#regusername").hide();
                $("#regconf").text("missing password confirmation").show();
                $("#reg_confirmation").css({"border": "1px solid red"});
                $("#reg_pw").css({"border": "1px solid grey"});
                $("#reg_username").css({"border": "1px solid grey"});
                $("#reg_confirmation").focus();
            }
            // password mismatch branch
            else if (data.error == "4") {
                $("#regpw").hide();
                $("#regusername").hide();
                $("#regconf").text("Password and confirmation do not match").show();
                $("#reg_confirmation").css({"border": "1px solid red"});
                $("#reg_pw").css({"border": "1px solid red"});
                $("#reg_username").css({"border": "1px solid grey"});
                $("#reg_pw").focus();
            }
            // username taken branch
            else if (data.error == "5") {
                $("#regpw").hide();
                $("#regconf").hide();
                $("#regusername").text("username already taken").show();
                $("#reg_username").css({"border": "1px solid red"});
                $("#reg_pw").css({"border": "1px solid grey"});
                $("#reg_confirmation").css({"border": "1px solid grey"});
                $("#reg_username").focus();
            }
            // success
            else {
                // redirect to the main page
                window.location.href = "/";
            }
        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // Execute when the quote form is submitted
    $("#quote").on("submit", function(event) {
        // Create a custom AJAX request
        $.ajax({
            data : {
                symbol: $("#quote_symbol").val()
            },
            type: "POST",
            url: "/quote"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            // missing or invalid input branch
            if (data.error) {
                $("#quote_symbol").css({"border": "1px solid red"});
                $("#quotesymbol").text("invalid or missing stock symbol").show();
                $("#quote_symbol").focus();
            }
            // success
            else {
                // return the price of the stock in a popup message (no redirect)
                $("#quotesymbol").hide();
                $("#quote_symbol").css({"border": "1px solid grey"});
                alert("The price of a "+ String(data.symbol) + " stock is "+ String(data.price) + " USD.");
            }

        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // Execute when the login form is submitted
    $("#login").on("submit", function(event) {
        // Create a custom AJAX request
        $.ajax({
            data : {
                username: $("#login_user").val(),
                password: $("#login_pw").val()
            },
            type: "POST",
            url: "/login"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            // missing username branch
            if (data.error == "1") {
                $("#login_user").css({"border": "1px solid red"});
                $("#loginpw").hide();
                $("#login_pw").css({"border": "1px solid grey"});
                $("#loginuser").text("missing username").show();
                $("#login_user").focus();
            }
            // missing password branch
            else if (data.error == "2") {
                $("#login_user").css({"border": "1px solid grey"});
                $("#loginuser").hide();
                $("#login_pw").css({"border": "1px solid red"});
                $("#loginpw").text("missing password").show();
                $("#login_pw").focus();
            }
            // invalid input branch
            else if (data.error == "3") {
                $("#login_user").css({"border": "1px solid red"});
                $("#loginpw").hide();
                $("#login_pw").css({"border": "1px solid red"});
                $("#loginuser").text("invalid username or password").show();
                $("#login_user").focus();
            }
            // redirect user to the main page upon success
            else {
                window.location.href = "/";
            }
        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // Execute when the "add recurring income/expense entry" form is submitted
    $("#auto_values").on("submit", function(event) {
        // Create a custom AJAX request
        $.ajax({
            data : {
                frequency: $("#frequency").val(),
                auto_type: $("#auto_type").val(),
                auto_title: $("#auto_title").val(),
                auto_amount: $("#auto_amount").val()
            },
            type: "POST",
            url: "/auto_values"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            console.log(data);
            // missing frequency branch
            if (data.error == "1") {
                $("#freq").text("Please select the frequency of the element").show();
                $("#autotype").hide();
                $("#autotitle").hide();
                $("#autoamount").hide();
                $("#frequency").css({"border": "1px solid red"});
                $("#auto_type").css({"border": "1px solid grey"});
                $("#auto_title").css({"border": "1px solid grey"});
                $("#auto_amount").css({"border": "1px solid grey"});
                $("#frequency").focus();
            }
            // missing type branch
            else if (data.error == "2") {
                $("#autotype").text("Please select the type of the element").show();
                $("#freq").hide();
                $("#autotitle").hide();
                $("#autoamount").hide();
                $("#frequency").css({"border": "1px solid grey"});
                $("#auto_type").css({"border": "1px solid red"});
                $("#auto_title").css({"border": "1px solid grey"});
                $("#auto_amount").css({"border": "1px solid grey"});
                // $("#auto_type").focus();
            }
            // missing title branch
            else if (data.error == "3") {
                $("#autotitle").text("Please enter the title of the element").show();
                $("#freq").hide();
                $("#autotype").hide();
                $("#autoamount").hide();
                $("#frequency").css({"border": "1px solid grey"});
                $("#auto_type").css({"border": "1px solid grey"});
                $("#auto_title").css({"border": "1px solid red"});
                $("#auto_amount").css({"border": "1px solid grey"});
                $("#auto_title").focus();
            }
            // missing or invalid amount branch
            else if (data.error == "4") {
                $("#autoamount").text("Please enter a valid amount for the element").show();
                $("#freq").hide();
                $("#autotitle").hide();
                $("#autotype").hide();
                $("#frequency").css({"border": "1px solid grey"});
                $("#auto_type").css({"border": "1px solid grey"});
                $("#auto_title").css({"border": "1px solid grey"});
                $("#auto_amount").css({"border": "1px solid red"});
                $("#auto_amount").focus();
            }
            // success
            else {
                // reload the main page to showcase changes
                location.reload();
            }
        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // if the "edit recurring element" button is clicked, display the
    // edit form and hide the delete form (in case the delete button was pressed before)
    $("#editauto").on("click", function() {
        $("#edit_auto").css({"display": "block"});
        $("#delete_auto").css({"display": "none"});
    });
    // if the "delete recurring element" button is clicked, display the
    // delete form and hide the edit form (in case the edit button was pressed before)
     $("#deleteauto").on("click", function() {
        $("#delete_auto").css({"display": "block"});
        $("#edit_auto").css({"display": "none"});
    });
    // if the "edit entry" button is clicked, display the
    // edit form and hide the delete form (in case the delete button was pressed before)
     $("#edithist").on("click", function() {
        $("#edit_hist").css({"display": "block"});
        $("#delete_hist").css({"display": "none"});
    });
    // if the "delete entry" button is clicked, display the
    // delete form and hide the edit form (in case the edit button was pressed before)
    $("#deletehist").on("click", function() {
        $("#delete_hist").css({"display": "block"});
        $("#edit_hist").css({"display": "none"});
    });
    // Execute when the "edit recurring income/expense entry" form is submitted
    $("#edit_auto").on("submit", function(event) {
        // Create a custom AJAX request
        $.ajax({
            data : {
                edit_id: $("#edit_id").val(),
                edit_type: $("#edit_type").val(),
                edit_title: $("#edit_title").val(),
                edit_amount: $("#edit_amount").val(),
                edit_frequency: $("#edit_frequency").val()
            },
            type: "POST",
            url: "/edit_auto"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            console.log(data);
            // missing ID branch
            if (data.error == "1"){
                $("#editid").text("Missing entry ID").show();
                $("#edit_id").css({"border": "1px solid red"});
                $("#edit_amount").css({"border": "1px solid grey"});
                $("#editamount").hide();
            }
            // Invalid ID branch
            else if (data.error == "2"){
                $("#editid").text("Invalid entry ID").show();
                $("#edit_id").css({"border": "1px solid red"});
                $("#edit_amount").css({"border": "1px solid grey"});
                $("#editamount").hide();
            }
            // success
            else {
                // reload page to showcase changes
                location.reload();
            }
        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // Execute when the "edit income/expense entry" form is submitted
    $("#edit_hist").on("submit", function(event) {
        // Create a custom AJAX request
        $.ajax({
            data : {
                edit_hist_id: $("#edit_hist_id").val(),
                edit_hist_type: $("#edit_hist_type").val(),
                edit_hist_title: $("#edit_hist_title").val(),
                edit_hist_amount: $("#edit_hist_amount").val(),
            },
            type: "POST",
            url: "/edit_hist"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            console.log(data);
            // missing entry ID branch
            if (data.error == "1"){
                $("#edithistid").text("Missing entry ID").show();
                $("#edit_hist_id").css({"border": "1px solid red"});
                $("#edit_hist_amount").css({"border": "1px solid grey"});
                $("#edithistamount").hide();
            }
            // invalid entry ID branch
            else if (data.error == "2"){
                $("#edithistid").text("Invalid entry ID").show();
                $("#edit_hist_id").css({"border": "1px solid red"});
                $("#edit_hist_amount").css({"border": "1px solid grey"});
                $("#edithistamount").hide();
            }
            // success
            else {
                // reload page to showcase changes
                location.reload();
            }
        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // Execute when the "delete all recurring entries" checkbox is clicked
    $("#delete_all_check").on("click", function() {
        // If the checkbox is checked, set its value to check
        if ($("#delete_all_check").is(":checked")){
            $("#delete_all_check").val("check");
        }
        // If the checkbox is unchecked, set its value to uncheck
        else {
            $("#delete_all_check").val("uncheck");
        }
    });
    // Execute when the "delete recurring income/expense entry" form is submitted
    $("#delete_auto").on("submit", function() {
        // create custom AJAX request
        $.ajax({
            data : {
                delete_id: $("#delete_id").val(),
                check: $("#delete_all_check").val()
            },
            type: "POST",
            url: "/delete_auto"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            console.log(data);
            // missing entry ID branch
            if (data.error == "1"){
                $("#delete_id").css({"border": "1px solid red"});
                $("#deleteid").text("Missing entry ID").show();
            }
            // Invalid entry ID branch
            else if (data.error == "2"){
                $("#delete_id").css({"border": "1px solid red"});
                $("#deleteid").text("Invalid entry ID").show();
            }
            // success
            else {
                //reload page to showcase changes
                location.reload();
            }
        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // Execute when the "delete all entries" checkbox is clicked
    $("#delete_all_check2").on("click", function() {
        // If the checkbox is checked change its value to check
        if ($("#delete_all_check2").is(":checked")){
            $("#delete_all_check2").val("check");
        }
        // If the checkbox is unchecked, change its value to uncheck
        else {
            $("#delete_all_check2").val("uncheck");
        }
    });
    // Execute when the "delete income/expense entry" form is submitted
    $("#delete_hist").on("submit", function() {
        // create custom AJAX request
        $.ajax({
            data : {
                delete_hist_id: $("#delete_hist_id").val(),
                check: $("#delete_all_check2").val()
            },
            type: "POST",
            url: "/delete_hist"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            console.log(data);
            // missing entry ID branch
            if (data.error == "1"){
                $("#delete_hist_id").css({"border": "1px solid red"});
                $("#deletehistid").text("Missing entry ID").show();
            }
            // invalid entry ID branch
            else if (data.error == "2"){
                $("#delete_hist_id").css({"border": "1px solid red"});
                $("#deletehistid").text("Invalid entry ID").show();
            }
            // success
            else {
                // reload page to showcase changes
                location.reload();
            }
        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // Execute when the "add income/expense entry" form is submitted
    $("#manual_values").on("submit", function(event) {
        // Create a custom AJAX request
        $.ajax({
            data : {
                manual_type: $("#manual_type").val(),
                manual_title: $("#manual_title").val(),
                manual_amount: $("#manual_amount").val()
            },
            type: "POST",
            url: "/manual_values"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            console.log(data);
            // missing type branch
            if (data.error == "1") {
                $("#manualtype").text("Please select the type of the element").show();
                $("#manualtitle").hide();
                $("#manualamount").hide();
                $("#manual_type").css({"border": "1px solid red"});
                $("#manual_title").css({"border": "1px solid grey"});
                $("#manual_amount").css({"border": "1px solid grey"});
                $("#manual_type").focus();
            }
            // missing title branch
            else if (data.error == "2") {
                $("#manualtitle").text("Please enter the title of the element").show();
                $("#manualtype").hide();
                $("#manualamount").hide();
                $("#manual_type").css({"border": "1px solid grey"});
                $("#manual_title").css({"border": "1px solid red"});
                $("#manual_amount").css({"border": "1px solid grey"});
                $("#manual_title").focus();
            }
            // missing or invalid amount branch
            else if (data.error == "3") {
                $("#manualamount").text("Please enter a valid amount for the element").show();
                $("#manualtitle").hide();
                $("#manualtype").hide();
                $("#manual_type").css({"border": "1px solid grey"});
                $("#manual_title").css({"border": "1px solid grey"});
                $("#manual_amount").css({"border": "1px solid red"});
                $("#manual_amount").focus();
            }
            // success
            else {
                // reload page to showcase changes
                location.reload();
            }
        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // when the "change starting balance" button is clicked show the appropriate form
    $("#editbalance").on("click", function() {
        $("#edit_balance").css({"display": "block"});
        $("#editbalance").css({"display": "none"});
    });
    // Execute when the "change starting balance" form is submitted
    $("#edit_balance").on("submit", function() {
        // create custom AJAX request
        $.ajax({
            data : {
                edit_balance_amount: $("#edit_balance_amount").val(),
            },
            type: "POST",
            url: "/edit_balance"
        })
        // when the request is done running check for valid input
        .done(function(data) {
            // missing or invalid amount branch
            if (data.error == "1") {
                $("#editbalanceamount").text("Missing or invalid amount").show();
                $("#edit_balance_amount").css({"border": "1px solid red"});
                $("#edit_balance_amount").focus();
            }
            // success
            else {
                // reload page to showcase changes
                location.reload();
            }
        });
        // disable the default HTML form submission mechanism
        event.preventDefault();
    });
    // Execute when the "delete all recurring entries" button is clicked
    $("#deleteallauto").on("click", function() {
        $("#delete_all_auto").css({"display": "block"});
        $("#deleteallauto").css({"display": "none"});
    });
    // Execute when the "delete all entries" button is clicked
    $("#deleteallhist").on("click", function() {
        $("#delete_all_hist").css({"display": "block"});
        $("#deleteallhist").css({"display": "none"});
    });
    // Execute when the "hide transaction history" button is clicked
    $("#hidetransactions").on("click", function() {
        $("#showtransactions").css({"display": "inline"});
        $("#transactions").css({"display": "none"});
        $("#hidetransactions").css({"display": "none"});
    });
    // Execute when the "show transaction history" button is clicked
     $("#showtransactions").on("click", function() {
        $("#hidetransactions").css({"display": "inline"});
        $("#transactions").css({"display": "inline"});
        $("#showtransactions").css({"display": "none"});
    });
});