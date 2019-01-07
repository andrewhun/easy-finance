from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Autovalue(models.Model):

	type_choices = (
		("Income", "Income"),
		("Expense", "Expense"),
		)

	frequency_choices = (
		("Daily", "Daily"),
		("Weekly", "Weekly"),
		("Monthly", "Monthly"),)

	value_type = models.CharField(max_length = 7, choices = type_choices)
	title = models.CharField(max_length = 50)
	amount = models.DecimalField(max_digits = 100, decimal_places = 2)
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	time = models.DateTimeField(auto_now_add = True)
	frequency = models.CharField(max_length = 7, choices = frequency_choices)

	def __str__(self):

		return f"{self.user}: {self.value_type} of {self.amount} USD recurring at {self.frequency} frequency"


class Transaction(models.Model):

	user = models.ForeignKey(User, on_delete = models.CASCADE)
	transaction_type = models.CharField(max_length = 4)
	stock = models.CharField(max_length = 4)
	price = models.DecimalField(max_digits = 100, decimal_places = 2)
	shares = models.IntegerField()
	time = models.DateTimeField(auto_now_add = True)

	def __str__(self):

		return (f"{self.user}: {self.transaction_type} transaction of "+
			f"{self.shares} shares of {self.stock} stock for {self.price} USD each")

class Portfolio(models.Model):

	user = models.ForeignKey(User, on_delete = models.CASCADE)
	stock = models.CharField(max_length = 4)
	current_price = models.DecimalField(max_digits = 100, decimal_places = 2)
	shares = models.IntegerField()
	value = models.DecimalField(max_digits = 100, decimal_places = 2)

	def __str__(self):

		return f"{self.user}: {self.shares} shares of {self.stock} stock worth {self.value}"

class Statement(models.Model):

	type_choices = (
		("Income", "Income"),
		("Expense", "Expense"),
		)

	statement_type = models.CharField(max_length = 7, choices = type_choices)
	title = models.CharField(max_length = 50)
	amount = models.DecimalField(max_digits = 100, decimal_places = 2)
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	time = models.DateTimeField(auto_now_add = True)

	def __str__(self):

		return f"{self.user}: {self.statement_type} of {self.amount} USD"

class Cash(models.Model):

	user = models.OneToOneField(User, on_delete = models.CASCADE)
	cash = models.DecimalField(max_digits = 100, decimal_places = 2)

	def __str__(self):

		return f"{self.cash}"

