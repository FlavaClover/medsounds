import os
import io
import logging
from http import HTTPStatus

import uvicorn
from mutagen.mp3 import MP3
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, UploadFile, Form, HTTPException

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine

from scheme import PodcastResponse

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

engine = create_async_engine(os.environ.get('DATABASE'))

app = FastAPI(description='Medsounds API', docs_url='/')


@app.get('/podcasts', tags=['Podcasts'], response_model=list[PodcastResponse])
async def read_podcast():
    async with engine.begin() as connection:
        query = await connection.execute(
            text(
                '''
                SELECT id, title, description, duration, likes, auditions FROM podcasts
                '''
            )
        )

        rows = query.mappings().all()

    return [PodcastResponse(**dict(row)) for row in rows]


@app.post('/podcasts', tags=['Podcasts'], response_model=PodcastResponse)
async def create_podcast(
        podcast: UploadFile,
        title: str = Form(),
        description: str = Form(),
):
    podcast_bytes = await podcast.read()
    audio = MP3(io.BytesIO(podcast_bytes))

    try:
        async with engine.begin() as connection:
            query = await connection.execute(
                text(
                    '''
                    INSERT INTO podcasts (title, description, duration, podcast) 
                    VALUES (:title, :description, :duration, :podcast)
                    RETURNING id, title, description, duration, likes, auditions
                    '''
                ),
                dict(
                    title=title, description=description,
                    duration=int(audio.info.length),
                    podcast=podcast_bytes
                )
            )

            row = query.mappings().one()
    except IntegrityError as e:
        if 'podcasts_title_key' in str(e):
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Title already exists')

    return PodcastResponse(**dict(row))


@app.get('/podcasts/{podcast_id}/audio/', tags=['Podcasts'])
async def get_audio_podcast(podcast_id: int):
    async with engine.begin() as connection:
        query = await connection.execute(
            text(
                '''
                SELECT podcast FROM podcasts WHERE id = :id
                '''
            ), dict(id=podcast_id)
        )

        podcast_bytes = query.scalar()

    if podcast_bytes:
        return StreamingResponse(io.BytesIO(podcast_bytes), media_type='audio/mp3')

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Podcast not found')


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, port=int(os.environ.get('HOST', 8001)))
