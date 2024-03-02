string = "string"

def hello():
    print("hi")

setattr(string, "hello", hello)

r = string.hello()
print(r)
