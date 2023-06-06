import aiohttp
import asyncio
from fake_useragent import UserAgent
from .transform import DataTransformer
import random


class HttpWorker(object):
    def __init__(self):
        self.user_agent = UserAgent()

    async def make_request(self, link, session, params=None, headers=False):
        if not headers:
            headers = {'User-Agent': self.user_agent.random}
            async with session.get(link, headers=headers, params=params) as response:
                return await response.text()
        else:
            async with session.get(link, params=params) as response:
                return await response.text()

    async def batch_request(self, request_list, params=None):
        async with aiohttp.ClientSession(cookies={'CONSENT': f'YES+cb.20210328-17-p0.en-GB+FX+{random.randint(100, 999)}'}) as session:
            tasks = [self.make_request(link, session, params) for link in request_list]
            return await asyncio.gather(*tasks)

    async def process_video_ids(self, video_ids, params):
        tasks = [self.process_video_id(vid_id, params) for vid_id in video_ids]
        return await asyncio.gather(*tasks)

    async def process_video_id(self, vid_id, params):
        try:
            transform = DataTransformer()
            channel_id = None
            async with aiohttp.ClientSession(cookies={'CONSENT': f'YES+cb.20210328-17-p0.en-GB+FX+{random.randint(100, 999)}'}) as session:
                html = await self.make_request(f'https://www.youtube.com/watch?v={vid_id}', session, params,
                                               headers=True)

                try:
                    channel_ids = transform.extract_pattern(data=html, beginning_pattern=r'/channel/',
                                                            end_pattern='"', get_all=True)

                except Exception as e:
                    channel_ids = []
                    print(f'https://www.youtube.com/watch?v={vid_id}')
            return channel_ids
        except Exception as e:
            print(e)
            return None

    async def process_channel_ids(self, channel_ids, params):
        tasks = [self.process_channel_id(ch_id, params) for ch_id in channel_ids]
        return await asyncio.gather(*tasks)

    async def process_channel_id(self, channel_id, params):
        try:
            transform = DataTransformer()
            async with aiohttp.ClientSession(
                    cookies={'CONSENT': f'YES+cb.20210328-17-p0.en-GB+FX+{random.randint(100, 999)}'}) as session:
                html = await self.make_request(f'https://www.youtube.com/channel/{channel_id}/about', session,
                                               params={'hl': 'en', 'gl': 'pl'}, headers=True)
                name = transform.extract_pattern(data=html, beginning_pattern=r'{"title":"', end_pattern='","')
                try:
                    description = transform.extract_pattern(html, r'name="description" content="', r'">')
                except:
                    description = "n/a"
                try:
                    image = transform.extract_pattern(html, r'rel="image_src" href="', r'">')
                except:
                    image = "n/a"
                try:
                    total_views = transform.extract_pattern(html, '"viewCountText":{"simpleText":"', '"}')
                except:
                    total_views = None

                subs = await transform.translate(transform.extract_pattern(data=html,
                                                                           beginning_pattern=r'}},"simpleText":"',
                                                                           end_pattern='"tvBanner"'))
                subs = transform.convert_to_int(subs)
                channel_country = transform.extract_pattern(data=html,
                                                            beginning_pattern=r'"country":{"simpleText":"',
                                                            end_pattern='"},')
                return {'channel_id': channel_id, 'name': name, 'subs': subs, 'country': channel_country,
                        'image': image, 'description': description, "total_views": total_views}
        except Exception as e:
            print(e)
            try:
                print(f"Error Channel link: https://www.youtube.com/channel/{channel_id}/about")
            except:
                print(f'Error ')
            return None

    async def process_channel_videos(self, channel_ids, params):
        tasks = [self.process_channel_video(ch_id, params) for ch_id in channel_ids]
        return await asyncio.gather(*tasks)

    async def process_channel_video(self, channel_id, params):
        try:
            transform = DataTransformer()
            async with aiohttp.ClientSession(
                    cookies={'CONSENT': f'YES+cb.20210328-17-p0.en-GB+FX+{random.randint(100, 999)}'}) as session:
                html = await self.make_request(f'https://www.youtube.com/channel/{channel_id}/videos', session,
                                               params={'hl': 'en', 'gl': 'pl'}, headers=True)

                try:
                    videos_views = transform.extract_pattern(html, '"viewCountText":{"simpleText":"', '"}', get_all=True)
                except:
                    videos_views = None

                try:
                    videos_time = transform.extract_pattern(html, '"publishedTimeText":{"simpleText":"', '"}',
                                                            get_all=True)
                except:
                    videos_time = None

                views_list = [transform.convert_to_int(views) for views in videos_views]
                time_list = [transform.convert_to_days(time) for time in videos_time]

                return {'channel_id': channel_id, "views_list": views_list, "time_list": time_list}
        except Exception as e:
            print(e)
            try:
                print(f"Error Channel link: https://www.youtube.com/channel/{channel_id}/about")
            except:
                print(f'Error ')
            return None