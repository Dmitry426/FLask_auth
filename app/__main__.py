from app import app
from app.core.config import FlaskSettings

settings = FlaskSettings()
app.run(
    host=settings.host,
    port=settings.port,
    debug=settings.debug,
)
