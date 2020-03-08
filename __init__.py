from gtts import gTTS
from yandex_dictionary import YandexDictionary, YandexDictionaryException

translater = YandexDictionary('dict.1.1.20200220T183914Z.ad078cb041516bce.6b3e7e48c087bb3b3f18013a1f8e0a05acbf9ac4')
a = translater.lookup('message', 'en', 'ru')
print (a)
import os
tts = gTTS(text='asd', lang='ru')
#tts.save("good.mp3")
os.system("mpg321 good.mp3")