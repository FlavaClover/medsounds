from pydantic import BaseModel


class PodcastResponse(BaseModel):
    id: int
    title: str
    description: str
    duration: int
    likes: int
    auditions: int
