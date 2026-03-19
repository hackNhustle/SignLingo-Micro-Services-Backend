from pydantic import BaseModel

class ChapterCompletion(BaseModel):
    subject_id: str
    chapter_id: str
