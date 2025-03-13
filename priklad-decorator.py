def upper(func):
    def wrapper():
        original_result = func()
        modified_result = original_result.upper()
        return modified_result
    return wrapper

@upper
def say_hello():
    return "hello"

if __name__ == "__main__":
    print(say_hello())