class Event:
    def __init__(self):
        self.handlers = []

    def register(self, handler):
        self.handlers.append(handler)

    def unregister(self, handler):
        self.handlers.remove(handler)
    
    def __call__(self, *args, **kwards):
        for handler in self.handlers:
            handler(*args, **kwards)


def vypis_jmeno(jmeno):
    print(f"Jméno: {jmeno}")

class Osoba:
    def __init__(self, jmeno):
        self.jmeno = None

    def __call__(self, jmeno):
        self.jmeno = jmeno
        print(f"Jméno: {self.jmeno}")

osoba = Osoba("Petr")
print(osoba.jmeno)
new_user_register = Event()
new_user_register.register(vypis_jmeno)
new_user_register.register(osoba)

new_user_register("Petr")
print(osoba.jmeno)