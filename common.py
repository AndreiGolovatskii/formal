def alignment(rows):
    maxlen = [0 for _ in rows[0]]
    for row in rows:
        for i in range(len(maxlen)):
            maxlen[i] = max(maxlen[i], len(row[i]))
    for row in rows:
        for i in range(len(maxlen)):
            row[i] = row[i].ljust(maxlen[i], " ")


class Eps(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __str__(self):
        return "eps"


eps = Eps()
