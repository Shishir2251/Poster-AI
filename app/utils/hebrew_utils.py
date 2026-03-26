from bidi.algorithm import get_display
import arabic_reshaper


def process_hebrew(text):

    reshaped = arabic_reshaper.reshape(text)

    return get_display(reshaped)