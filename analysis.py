import profile

from main import main

def test():
    app = main()
    app.exit()
    app.exec()

profile.run("test()")