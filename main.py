import asyncio
import csv
import os
import jsonpickle

from flask import Flask,  jsonify
from flask_cors import CORS

import python_package


app = Flask("app")
CORS(app)


os.environ['GOOGLE_API_KEY'] = 'AIzaSyBi4Y4V0EadlXkw5f9Nq6LFOXVodB-OmRg'


async def create_response(data):
    """Creates and returns a response object."""
    async with app.test_request_context('/'):
        response = jsonify({"data": data})
        response.headers.add('Access-Control-Allow-Origin', '*')
    return response


async def search_yt(request):
    """Searches YouTube based on country and keyword."""
    country = request.args.get('country')
    channels = request.args.get("channels")

    # Load country list
    country_list = [*csv.DictReader(open("assets/country_language.csv"))]
    country_dict = list(filter(lambda d: d['country_name'] == country, country_list))

    http_worker = python_package.HttpWorker()
    transform = python_package.DataTransformer()

    params = {
        "hl": country_dict[0]['language_code'],
        "gl": country_dict[0]['country_code']
    }

    channels_list = transform.string_to_list(channels)

    # Translate keyword
    urls = await transform.build_urls(channels_list, country_dict)

    htmls = await http_worker.batch_request(urls, params={"hl": "en", "gl": "uk"})

    video_ids = await transform.extract_video_ids(htmls)
    video_ids_flat_list = await transform.async_flatten_nested_lists(video_ids)
    video_ids_flat_list_unique = list(set(video_ids_flat_list))

    # Analyze the videos
    channel_id_list = await http_worker.process_video_ids(video_ids_flat_list_unique, params=params)
    channel_ids_flat_list = await transform.async_flatten_nested_lists(channel_id_list)
    channel_id_list_unique = list(set(channel_ids_flat_list))
    channel_id_list_unique_cleared = await transform.clear_channel_list(channel_id_list_unique)

    channel_data_list = await http_worker.process_channel_ids(channel_id_list_unique_cleared, params)

    channel_videos_list = await http_worker.process_channel_videos(channel_id_list_unique, params)

    channels_data_merged = transform.merge_lists_on_key(list1=channel_data_list, list2=channel_videos_list,
                                                        key="channel_id")

    data = []

    data.extend(channels_data_merged)

    # Filter out None values
    data = [x for x in data if x is not None]
    print(data)
    return jsonpickle.encode(data)


class MockRequest:
    """Mock Request class."""
    def __init__(self, country, channels):
        self.args = {'country': country, 'channels': channels}


def create_response(data):
    """Creates and returns a response object."""
    print(type(data))  # Check the data type
    with app.app_context():
        response = jsonify({"data": data})
        response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/channel_data/<country>/<channels>', methods=['GET'])
def scrape_youtube_data(request):
    """Scrapes YouTube data and returns a response."""
    country = request.args.get('country')
    channels = request.args.get('channels')
    mock_request = MockRequest(country=country, channels=channels)
    data = asyncio.run(search_yt(request=mock_request))
    response = create_response(data)
    return response


if __name__ == "__main__":
    country = "France"
    channels = "['UC855lGKTrQOUCuWxiv--OxA', 'UC855lGKTrQOUCuWxiv--OxA', 'UC2mwsE-87Hfh9ZmSrqBqNIg', 'UC5sZPItEIDwOlCmSBbWzRiw', 'UCgN6VM0MKJ1W7EwjX9qIPhg', 'UCBbuMYqQY05m27gSccTks9Q', 'UCes5UfgRhGeVWt1a9oEGoyg', 'UC0xNbxurzRU4Q9JAKv9oLJg', 'UC37s46-H1Mlv88HX8f7aHKQ', 'UC-82Z55nusYZb9_8V6Pmmyw', 'UC0xNbxurzRU4Q9JAKv9oLJg', 'UCes5UfgRhGeVWt1a9oEGoyg', 'UCGKkc1W8aQ3Z4yHE89Bc4fg', 'UCs6mVnsiDrJL9CbuiemXa3w', 'UC5sZPItEIDwOlCmSBbWzRiw', 'UC2mwsE-87Hfh9ZmSrqBqNIg', 'UCBbuMYqQY05m27gSccTks9Q', 'UC855lGKTrQOUCuWxiv--OxA', 'UCUP4XFMrsJG5_AbG6ZYBVFA', 'UCF8l-YD3e3LK1LnxFhNaNDQ', 'UCs5IxVpqCYv7xiPsclF8mFA', 'UC2mwsE-87Hfh9ZmSrqBqNIg'"
    mock_request = MockRequest(country=country, channels=channels)
    result = scrape_youtube_data(request=mock_request)
    print(result)
