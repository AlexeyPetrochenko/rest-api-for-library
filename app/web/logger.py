import logging


def setup_logging(level: int = logging.INFO) -> None:
    log_format = (
        "[%(asctime)s.%(msecs)03d] "
        "%(module)10s:%(lineno)-4d "
        "%(levelname)-7s - %(message)s"
    )
    logging.basicConfig(
        level=level, datefmt="%Y-%m-%d %H:%M:%S", format=log_format
    )

    logging.getLogger("uvicorn.error").propagate = False
    logging.getLogger("uvicorn.access").propagate = False
    logging.getLogger("uvicorn").propagate = False
    logging.getLogger("uvicorn.error").disabled = True
