import uvicorn

from src.conf.app_instance import create_app
from src.conf.logging import LOG_CONFIG
from src.conf.settings import settings


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.value.lower(),
        log_config=LOG_CONFIG,
        loop="uvloop",
    )
