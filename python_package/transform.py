import re
import asyncio
import urllib.parse
from googletrans import Translator

class DataTransformer:
    def __init__(self):
        self.translator = Translator()

    def extract_pattern(self, data, beginning_pattern=None, end_pattern=None, pattern=None, get_all=False):
        if not pattern:
            pattern = f'{beginning_pattern}(.*?){end_pattern}'
            result = re.findall(pattern, data, re.DOTALL)
        else:
            result = re.findall(pattern, data, re.DOTALL)
        if get_all:
            return result
        elif not get_all:
            return result[0]

    def string_to_list(self, string_list):
        # Remove the brackets and split by comma
        parts = string_list[1:-1].split(', ')

        # For each part, remove the quotes
        list_items = [part[1:-1] for part in parts]

        return list_items

    def transform_keywords(self, keyword_list_string):
        return [word.strip() for word in keyword_list_string.split(",")]

    async def translate(self, text, lang='en'):
        return self.translator.translate(text, dest=lang).text

    async def build_urls(self, channels, country_dict):
        return [f"https://www.youtube.com/channel/{urllib.parse.quote(channel_id)}/videos" for channel_id in channels]

    async def _extract_video_ids_from_html(self, html):
        videos = re.findall(r'"videoId":"(.*?)"', html)
        return list(set([v_id[0:11] for v_id in videos]))

    async def extract_video_ids(self, htmls):
        return await asyncio.gather(*[self._extract_video_ids_from_html(html) for html in htmls])

    async def async_flatten_nested_lists(self, nested_lists):
        return [item for sublist in nested_lists for item in sublist]

    def build_channel_url(self, channel_id):
        return f'https://www.youtube.com/channel/{channel_id}/about'

    async def clear_channel_list(self, channel_list):
        return [channel for channel in channel_list if "videos" not in channel and "about" not in channel]

    async def extract_and_translate_channel_data(self, html):
        name = re.findall(r'{"title":"(.*?)","', html)[0]
        description = self.extract_pattern(html, r'name="description" content="', r'">') or "n/a"
        image = self.extract_pattern(html, r'rel="image_src" href="', r'">') or "n/a"
        subs = await self.translate(re.findall(r'}},"simpleText":"(.*?)"tvBanner"', html)[0])
        subs = self.convert_to_int(subs)
        channel_country = await self.translate(re.findall(r'"country":{"simpleText":"(.*?)"},', html)[0])

        return name, description, image, subs, channel_country

    def remove_trailing_comma(self, value):
        return value.rstrip(",")

    def convert_to_int(self, value):
        units = {"thousand": 1000, "million": 1000000, "billion": 1000000000, "k": 1000, "K": 1000, "M": 1000000,
                 "m": 1000000}
        try:
            # remove any comma from the value
            value = value.replace(',', '')
            multiplier = 1
            # Check if the value contains any unit and replace it
            for unit in units:
                if unit in value:
                    value = value.replace(unit, "")
                    multiplier = units[unit]
                    break
            # Use regex to extract numeric value from string
            numeric_value = re.search("[-+]?\d*\.\d+|\d+", value).group()
            # Multiply extracted value with the appropriate multiplier
            numeric_value = float(numeric_value) * multiplier
            # Convert extracted value to int
            return int(numeric_value)
        except:
            print(f"Unable to convert {value} to int.")

    def convert_to_days(self, time_str):
        units = {"minute": 1 / 1440, "hour": 1 / 24, "day": 1, "week": 7, "month": 30, "year": 365}
        time_value, unit = time_str.split(' ')[0], time_str.split(' ')[1]
        # Handle plural units
        if unit.endswith('s'):
            unit = unit[:-1]
        if unit in units:
            days = int(time_value) * units[unit]
            return days
        else:
            print(f"Unable to convert {time_str} to days.")
            return None

    def merge_lists_on_key(self, list1, list2, key):
        """
        Merge two lists of dictionaries based on a common key.

        Parameters:
        - list1: The first list of dictionaries.
        - list2: The second list of dictionaries.
        - key: The key on which to merge the dictionaries.

        Returns:
        - A list of merged dictionaries.
        """

        # Remove None elements from the lists
        list1 = [i for i in list1 if i]
        list2 = [i for i in list2 if i]

        key_to_data = {d[key]: d.copy() for d in list1}
        for d in list2:
            if d[key] in key_to_data:
                key_to_data[d[key]].update(d)
        return list(key_to_data.values())
