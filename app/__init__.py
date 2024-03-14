from flask import Flask
from app import views

def Site():
    site = Flask(__name__, template_folder='views/templates', static_folder='views/static')
    views.apply(site)

    return site
