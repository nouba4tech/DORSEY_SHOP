"""
Extensions Flask pour DORSEY-SHOP
Ce fichier permet d'éviter les imports circulaires
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
try:
	from flask_babel import Babel
except Exception:
	# Provide a minimal fallback for environments without Flask-Babel
	class Babel:  # type: ignore
		def init_app(self, app):
			return None

		def localeselector(self, fn):
			return fn

# Initialiser les extensions sans l'application
# Elles seront initialisées dans create_app
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
babel = Babel()