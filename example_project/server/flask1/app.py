import sys
import os

from flask import Flask
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '../../../'))
sys.path.append(root)

from simpleapi import Route
from handlers import MyAPI

app = Flask(__name__)

app.route('/api/', methods=['GET', 'POST'])(Route(MyAPI, framework='flask'))

if __name__ == '__main__':
    app.run(debug=True)