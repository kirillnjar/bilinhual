import json

from yandex_dictionary import YandexDictionary

translater = YandexDictionary('dict.1.1.20200220T183914Z.ad078cb041516bce.6b3e7e48c087bb3b3f18013a1f8e0a05acbf9ac4')
right_word_info = json.loads(translater.lookup('false', 'en', 'ru'))['def'][0]['tr']
print(right_word_info)