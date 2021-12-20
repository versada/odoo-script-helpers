Odoo helper scripts
===================

Tested with Python 3.6, 3.9.

Note, needs to run with interactive mode ``(python -i)``.

record.py
=========

Supports ``read(<list of fields>)`` and ``write(<dict of values>)`` commands in the interactive mode.

Example:

```
$ python -i record.py http://172.19.0.3:8069 database_name sale.order 20
Please enter the password of 'admin' Odoo user:
>>> data = read(['date_order'])
>>> data
[{'id': 20, 'date_order': '2021-12-16 11:20:58'}]
>>> date_order = data[0]['date_order']
>>> import datetime
>>> date_order_new = datetime.datetime.strptime(date_order, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=1)
>>> write({'date_order': date_order_new.strftime('%Y-%m-%d %H:%M:%S')})
True
```

Credits
=======

* Naglis Jonaitis
* Paulius Sladkevičius
