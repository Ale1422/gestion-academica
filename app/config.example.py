import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://usuario:contraseña@hostBaseDeDatos/nombreDB')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
