# coding: utf-8

from neptulon.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
