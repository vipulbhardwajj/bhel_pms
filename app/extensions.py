"""
app/extensions.py
------------------
Instantiates all Flask extensions in a single module. Extensions are created
here (without an app bound yet) and initialised later inside the application
factory (`create_app`) using `extension.init_app(app)`. This pattern avoids
circular imports between models, routes and the app factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()

# Configure Flask-Login defaults
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access the BHEL Project Monitoring System."
login_manager.login_message_category = "warning"
