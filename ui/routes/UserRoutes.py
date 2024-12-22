from ui.WebUI import WebUI
from ui.LoginUI import LoginUI
from flask import render_template, request, session, redirect, url_for, flash
from logic.User import User
from data.Database import Database

class UserRoutes:
    __app = WebUI.get_app()

    @staticmethod
    @__app.route("/login")
    def login():
        return render_template("user/login.html")
      