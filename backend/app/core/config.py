from pydantic import BaseModel

class Settings:
    app_name = "Macedonian OCR Platform"
    app_version = "0.1.0"
    debug = True

settings = Settings()