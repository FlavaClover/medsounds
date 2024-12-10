import io
import os
import json
import uuid
import logging
from http import HTTPStatus
from typing import Literal, Annotated

import uvicorn
from mutagen.mp3 import MP3
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, Form, HTTPException, Response, Header

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine

from scheme import PodcastResponse, CreatePostRequest, CreatePostResponse, GetPostResponse, Post

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

engine = create_async_engine(os.environ.get('DATABASE'))
images_dir = os.path.abspath(os.environ.get('IMAGES_DIR', './images'))
images_dir_for_db = os.path.abspath(os.environ.get('IMAGES_DIR_FOR_DB', './images'))

app = FastAPI(
    description='Medsounds API',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/podcasts', tags=['Podcasts'], response_model=list[PodcastResponse])
async def all_podcasts(browser_ident: Annotated[str, Header()]):
    async with engine.begin() as connection:
        query = await connection.execute(
            text(
                '''
                    SELECT 
                        podcasts.id, 
                        title, 
                        description, 
                        duration,
                        auditions,
                        
                        CASE 
                            WHEN array_agg(t.tag)::text = '{NULL}' THEN null
                            ELSE string_agg(t.tag, ',')
                        END tags
                    FROM podcasts
                    left join podcast_tags t on podcasts.id = t.podcast_id
                    GROUP BY podcasts.id, title, description, duration, auditions
                '''
            )
        )

        rows = [dict(r) for r in query.mappings().all()]
        for r in rows:
            query = await connection.execute(
                text(
                    '''
                    SELECT COUNT(*) FROM podcast_likes WHERE podcast_id = :pid
                    '''
                ), dict(pid=r['id'])
            )
            r['likes'] = query.scalar()

        for r in rows:
            query = await connection.execute(
                text(
                    '''
                    SELECT COUNT(*) FROM podcast_likes WHERE podcast_id = :pid 
                                                             AND browser_ident = :bi
                    '''
                ), dict(pid=r['id'], bi=browser_ident)
            )
            r['liked'] = query.scalar() == 1

    return [PodcastResponse(**dict(row)) for row in rows]


@app.post('/podcasts', tags=['Podcasts'], response_model=PodcastResponse)
async def create_podcast(
        podcast: UploadFile,
        image: UploadFile,
        title: str = Form(),
        description: str = Form(),
        tags: list[str] = Form()
):
    podcast_bytes = await podcast.read()
    image_bytes = await image.read()
    audio = MP3(io.BytesIO(podcast_bytes))

    try:
        async with engine.begin() as connection:
            query = await connection.execute(
                text(
                    '''
                    INSERT INTO podcasts (title, description, duration, podcast, image) 
                    VALUES (:title, :description, :duration, :podcast, :image)
                    RETURNING id, title, description, duration, likes, auditions
                    '''
                ),
                dict(
                    title=title, description=description,
                    duration=int(audio.info.length),
                    podcast=podcast_bytes,
                    image=image_bytes
                )
            )

            row = query.mappings().one()

            await connection.execute(
                text(
                    '''
                    INSERT INTO podcast_tags (tag, podcast_id) VALUES (:tag, :pid)
                    '''
                ),
                [
                    dict(tag=t, pid=row['id'])
                    for t in tags
                ]
            )

    except IntegrityError as e:
        if 'podcasts_title_key' in str(e):
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Title already exists')

    return PodcastResponse(**dict(row), tags=tags)


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


@app.get('/podcasts/{podcast_id}/image/', tags=['Podcasts'])
async def get_image_podcast(podcast_id: int):
    async with engine.begin() as connection:
        query = await connection.execute(
            text(
                '''
                SELECT image FROM podcasts WHERE id = :id
                '''
            ), dict(id=podcast_id)
        )

        image_bytes = query.scalar()

    if image_bytes:
        return StreamingResponse(io.BytesIO(image_bytes), media_type='image/png')

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Podcast not found')


@app.post('/podcasts/{podcast_id}/like-unlike/', tags=['Podcasts'])
async def like_unlike_podcast(podcast_id: int, browser_ident: Annotated[str, Header()]):
    async with engine.begin() as connection:
        query = await connection.execute(
            text(
                '''
                SELECT COUNT(*) FROM podcast_likes WHERE podcast_id = :pid 
                                                         AND browser_ident = :bi
                '''
            ), dict(pid=podcast_id, bi=browser_ident)
        )

        if query.scalar() == 1:
            await connection.execute(
                text(
                    '''
                    DELETE FROM podcast_likes WHERE podcast_id = :pid AND browser_ident = :bi
                    '''
                ), dict(pid=podcast_id, bi=browser_ident)
            )
        else:
            await connection.execute(
                text(
                    '''
                    INSERT INTO podcast_likes (browser_ident, podcast_id) VALUES (:bi, :pid)
                    '''
                ), dict(pid=podcast_id, bi=browser_ident)
            )

    return Response(status_code=HTTPStatus.OK)


@app.post('/podcasts/{podcast_id}/auditions', tags=['Podcasts'])
async def increase_auditions(podcast_id: int):
    async with engine.begin() as connection:
        await connection.execute(
            text(
                '''
                UPDATE podcasts SET auditions = auditions + 1
                WHERE id = :id
                '''
            ), dict(id=podcast_id)
        )

    return Response(status_code=HTTPStatus.OK)


@app.post('/posts', response_model=CreatePostResponse, tags=['Posts'])
async def create_post(
        image: UploadFile,
        title: str = Form(),
        content: str = Form(),
        tags: list[str] = Form(),
):
    image_id = uuid.uuid4().hex
    image_path = images_dir + f'/{image_id}.png'

    with open(image_path, 'wb') as file:
        file.write(await image.read())

    image_path_for_save = images_dir_for_db + f'/{image_id}.png'

    async with engine.begin() as connection:
        query = await connection.execute(
            text(
                '''
                INSERT INTO posts (title, content, image) 
                VALUES (:title, :content, :image)
                RETURNING id
                '''
            ),
            dict(title=title, content=content, image=image_path_for_save)
        )

        post_id = query.scalar()

        await connection.execute(
            text(
                '''
                INSERT INTO post_tags (tag, post_id) VALUES (:tag, :pid)
                '''
            ),
            [
                dict(tag=t, pid=post_id)
                for t in tags
            ]
        )

    return CreatePostResponse(post_id=post_id)


@app.get('/posts', response_model=GetPostResponse, tags=['Posts'])
async def all_posts(browser_ident: Annotated[str, Header()]):
    async with engine.begin() as connection:
        query = await connection.execute(
            text(
                '''
                SELECT 
                    posts.id as post_id,
                    title,
                    content,
                    extract(epoch from created_at)::int as created_at,
                    image,
                    CASE 
                        WHEN array_agg(t.tag)::text = '{NULL}' THEN null
                        ELSE string_agg(t.tag, ',')
                    END tags
                FROM posts
                left join post_tags t on posts.id = t.post_id
                GROUP BY posts.id, title, content, extract(epoch from created_at), image
                '''
            )
        )

        rows = [dict(r) for r in query.mappings().all()]
        for r in rows:
            query = await connection.execute(
                text(
                    '''
                    SELECT COUNT(*) FROM post_likes WHERE post_id = :pid
                    '''
                ), dict(pid=r['post_id'])
            )
            r['likes'] = query.scalar()

        for r in rows:
            query = await connection.execute(
                text(
                    '''
                    SELECT COUNT(*) FROM post_likes WHERE post_id = :pid 
                                                             AND browser_ident = :bi
                    '''
                ), dict(pid=r['post_id'], bi=browser_ident)
            )
            r['liked'] = query.scalar() == 1

    return GetPostResponse(posts=[Post(**dict(r)) for r in rows])


@app.post('/posts/{post_id}/like-unlike/', tags=['Posts'])
async def like_unlike_post(post_id: int, browser_ident: Annotated[str, Header()]):
    async with engine.begin() as connection:
        query = await connection.execute(
            text(
                '''
                SELECT COUNT(*) FROM post_likes WHERE post_id = :pid 
                                                         AND browser_ident = :bi
                '''
            ), dict(pid=post_id, bi=browser_ident)
        )

        if query.scalar() == 1:
            await connection.execute(
                text(
                    '''
                    DELETE FROM post_likes WHERE podcast_id = :pid AND browser_ident = :bi
                    '''
                ), dict(pid=post_id, bi=browser_ident)
            )
        else:
            await connection.execute(
                text(
                    '''
                    INSERT INTO post_likes (browser_ident, post_id) VALUES (:bi, :pid)
                    '''
                ), dict(pid=post_id, bi=browser_ident)
            )

    return Response(status_code=HTTPStatus.OK)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
        port=int(os.environ.get('PORT', 8001)),
        host=os.environ.get('HOST', '0.0.0.0')
    )
