import pycountry
import gettext

from django.conf import settings
from django.core.cache import cache


class CountryData:
    CACHE_KEY = 'countrydata'

    def __init__(self, languages: list):
        self.languages = languages
        self.__data = []

    def translate_country(self, country):
        names = {}
        for language in self.languages:
            if language != 'en':
                lang = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=[language])
                lang.install()
                _ = lang.gettext
                names[language] = _(country.name)
            else:
                names[language] = country.name

        return names

    def get_country_info(self, country):
        return {
            'alpha_2': country.alpha_2,
            'phone_code': country.numeric,
        }

    def __create_dict(self):
        self.__data = []
        for country in list(pycountry.countries):
            country_info = self.get_country_info(country)
            country_info['name_language'] = self.translate_country(country)
            self.__data.append(country_info)
        return self.__data

    def get_data(self):
        if not self.__data:
            from_cache = cache.get(self.CACHE_KEY)
            if from_cache is None:
                self.__data = self.__create_dict()
            else:
                self.__data = from_cache

        return self.__data
