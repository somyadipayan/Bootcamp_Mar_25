class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///grocerystore.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_PASSWORD = "1"
    JWT_SECRET_KEY = "super-secre-dbswaidgbi"