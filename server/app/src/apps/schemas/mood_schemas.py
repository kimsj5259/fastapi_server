from ..models.mood_model import MoodMicroStatus
from ...core.decorators.partial import optional

@optional
class IMoodMicroRead(MoodMicroStatus):
    pass

class IMoodMicroCreate(MoodMicroStatus):
    pass

class IMoodMicroUpdate(MoodMicroStatus):
    pass