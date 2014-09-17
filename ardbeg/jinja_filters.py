from table_fu import Datum
'''
table_fu objects have to be handled a bit specially.
Generally, check they are Datum class, and then handle with .value
'''
def currency(value):
	if isinstance(value,Datum):
		return "${:,}".format(int(value.value))
	else:
		return "${:,}".format(int(value))
def comma(value):
	if isinstance(value,Datum):
		return "{:,}".format(int(value.value))
	else:
		return "{:,}".format(int(value))

'''
Register functions in the func_list.
'''
func_list = [currency,comma]

