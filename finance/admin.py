from django.contrib import admin
from .models import Autovalue, Transaction, Portfolio, Statement, Cash
# Register your models here.
admin.site.register(Autovalue)
admin.site.register(Transaction)
admin.site.register(Portfolio)
admin.site.register(Statement)
admin.site.register(Cash)