from typing import Union

class CustomChar():
    def __init__(self, char: list[int], aliases: Union[list[str], str]) -> None:
        self.char = char
        if isinstance(aliases, str):
            self.aliases = [aliases]
        else:
            self.aliases = aliases

class ROM():
    def __init__(self, default_custom_chars: list[CustomChar], available_chars: Union[str, list[str]], replaceable_chars: str) -> None:
        if isinstance(default_custom_chars, list) == False:
            raise TypeError('default_custom_chars argument must be a list of CustomChar.')
        if [isinstance(x, CustomChar) for x in default_custom_chars].count(False) > 0:
            raise TypeError('All items in default_custom_chars list argument must be of type CustomChar.')
        if len(default_custom_chars) > 8:
            raise ValueError('Can only define up to 8 custom characters.')
        self._default_custom_chars = default_custom_chars
        if isinstance(available_chars, str):
            self._available_chars = available_chars
        elif isinstance(available_chars, list):
            self._available_chars=''.join(available_chars)
        else:
            raise TypeError('available_chars argument must be either a string of chars or a list of strings containing chars.')
        if isinstance(replaceable_chars, str) == False:
            raise TypeError('replaceable_chars argument must be a string of chars.')
        self._replaceable_chars = replaceable_chars
    
    @property
    def default_custom_chars(self) -> list[CustomChar]:
        return self._default_custom_chars
    
    @property
    def available_chars(self) -> str:
        return self._available_chars
    
    @property
    def replaceable_chars(self) -> str:
        return self._replaceable_chars