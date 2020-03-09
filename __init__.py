from datetime import timedelta

a = None
if a is None:
    a = timedelta(minutes=30)
a = a + timedelta(minutes=30)

print(a)