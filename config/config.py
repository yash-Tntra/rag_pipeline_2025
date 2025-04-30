from enum import Enum
from . import  env

class OpenAi(Enum):
    OPEN_API_KEY = env.str("OPEN_API_KEY")



