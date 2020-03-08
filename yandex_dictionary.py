# coding: utf-8

import requests
import requests.exceptions


class YandexDictionaryException(Exception):
    error_codes = {
        401: "ERR_KEY_INVALID",
        402: "ERR_KEY_BLOCKED",
        403: "ERR_DAILY_REQ_LIMIT_EXCEEDED",
        404: "ERR_DAILY_CHAR_LIMIT_EXCEEDED",
        413: "ERR_TEXT_TOO_LONG",
        422: "ERR_UNPROCESSABLE_TEXT",
        501: "ERR_LANG_NOT_SUPPORTED",
        503: "ERR_SERVICE_NOT_AVAIBLE",
    }

    def __init__(self, status_code, *args, **kwargs):
        message = self.error_codes.get(status_code)
        super(YandexDictionaryException, self).__init__(
            message, *args)


class YandexDictionary(object):
    api_url = "https://dictionary.yandex.net/api/{version}/{service}/{endpoint}"
    api_version = "v1"
    api_endpoints = {
        "langs": "getLangs",
        "lookup": "lookup",
    }
    api_services = {
        'xml': 'dicservice',
        'json': 'dicservice.json'
    }

    def __init__(self, key=None, format='json'):
        if not key:
            raise YandexDictionaryException(401)
        self.api_key = key
        self.api_format = format

    def url(self, endpoint):
        return self.api_url.format(version=self.api_version,
                                   endpoint=self.api_endpoints[endpoint],
                                   service=self.api_services[self.api_format])

    @property
    def directions(self):
        try:
            response = requests.get(
                self.url("langs"), params={"key": self.api_key})
        except requests.exceptions.ConnectionError:
            raise YandexDictionaryException(YandexDictionaryException.error_codes[503])

        status_code = response.status_code
        if status_code != 200:
            raise YandexDictionaryException(status_code)
        return response.text

    @property
    def langs(self):
        if self.api_format == 'json':
            import json
            return set(x.split("-")[0] for x in json.loads(self.directions))
        else:
            from lxml import etree
            return set(x.text.split("-")[0] for x in etree.fromstring(self.directions.encode('utf-8')))

    def lookup(self, text, from_lang, to_lang):
        data = {
            "text": text,
            "lang": '%s-%s' % (from_lang, to_lang),
            "key": self.api_key
        }
        try:
            response = requests.post(self.url("lookup"), data=data)
        except ConnectionError:
            raise YandexDictionaryException(503)
        status_code = response.status_code
        if status_code != 200:
            raise YandexDictionaryException(status_code)
        return response.text

if __name__ == "__main__":
    import doctest
    doctest.testmod()