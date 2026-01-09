import logging
from logging.handlers import TimedRotatingFileHandler

class AgentLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger()
        return cls._instance

    def _init_logger(self):
        # default config
        cfg = {
            "log_dir": "logs",
            "filename": "agent_trace.log",
            "level": "INFO",
            "rotation": "monthly",  # we will implement monthly
            "backup_count": 12,
        }

        from pathlib import Path
        Path(cfg["log_dir"]).mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("JobSearchAgent")
        self.logger.setLevel(getattr(logging, cfg["level"].upper()))
        self.logger.propagate = False

        log_file = f"{cfg['log_dir']}/{cfg['filename']}"
        handler = TimedRotatingFileHandler(
            log_file,
            when="midnight",
            interval=1,
            backupCount=cfg["backup_count"]
        )
        handler.suffix = "%m.%Y"  # monthly
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)
