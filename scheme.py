from typing import Any

from pydantic import BaseModel, Field


class Podcast(BaseModel):
    id: int
    title: str
    description: str
    duration: int
    likes: int
    auditions: int
    tags: list[str]
    liked: bool
    image: str
    podcast: str

    def __init__(self, **data):
        if data['tags'] is None:
            data['tags'] = []
        if isinstance(data['tags'], str):
            data['tags'] = data['tags'].split(',')

        super().__init__(**data)


class GetPodcastResponse(BaseModel):
    podcasts: list[Podcast]



class CreatePostRequest(BaseModel):
    title: str
    content: str
    tags: list[str]
    image: str | bytes


class CreatePostResponse(BaseModel):
    post_id: str | int


class Post(BaseModel):
    post_id: str | int
    created_at: str | int
    title: str
    content: str
    tags: list[str]
    image: str
    likes: int
    liked: bool

    def __init__(self, **data):
        if data['tags'] is None:
            data['tags'] = []
        if isinstance(data['tags'], str):
            data['tags'] = data['tags'].split(',')

        super().__init__(**data)


class GetPostResponse(BaseModel):
    posts: list[Post]
