import os
import typing

import mypy_extensions

__all__ = ("ConfigError", "Config", "config")


UNSET = object()


SchemaItem = mypy_extensions.TypedDict(
    "SchemaItem",
    {
        "key": str,
        "default": object,
        "type": typing.Type[typing.Any],
        "subtype": typing.Type[typing.Any],
        "mapper": typing.Optional[typing.Callable[[object], object]],
    },
    total=False,
)

Schema = typing.Mapping[str, typing.Union[typing.Type[typing.Any], SchemaItem]]


class ConfigError(Exception):
    """
    Exception to throw on configuration errors.
    """


class Config:
    """
    Config environment parser.

    This class allows chosen configuration values to be extracted from the
    processes environment variables and converted into the relevant types.

    .. code-block:: python

        parser = Config()

        config = parser({
            'DEBUG': {
                'type': bool,
                'default': False,
            },
            'SECRET_KEY': str,
        })

    The above will populate the :code:`config` variable with two values,
    :code:`DEBUG` will be populated with a :class:`bool` from the environment
    variable of the same  name, throwing an exception on invalid values and
    defaulting to :data:`False` when none is provided, and :code:`SECRET_KEY`
    will be a :class:`str` and throw a :exc:`ConfigError` when no value is
    found in the environment.

    An optional :code:`environ` param can be  passed in order to override the
    environment.

    :param environ: environment dictionary, defaults to :data:`os.environ`

    """

    TRUE_STRINGS = ("t", "true", "on", "ok", "y", "yes", "1")

    def __init__(
        self, environ: typing.Optional[typing.Mapping[str, str]] = None
    ) -> None:
        self.environ: typing.Mapping[str, str] = (
            environ if environ is not None else os.environ
        )

    def __call__(self, schema: Schema) -> typing.Dict[str, typing.Any]:
        """
        Parse the environment according to a schema.

        :param schema: the schema to parse
        :return: a dictionary of config values

        """
        result = {}

        for key, item in schema.items():
            if callable(item):
                result[key] = self.get(key=key, type_=item)

                continue

            result[key] = self.get(
                key=item.get("key", key),
                default=item.get("default", UNSET),
                type_=item.get("type", str),
                subtype=item.get("subtype", str),
                mapper=item.get("mapper", None),
            )

        return result

    def parse(
        self,
        value: str,
        type_: typing.Type[typing.Any] = str,
        subtype: typing.Type[typing.Any] = str,
    ) -> typing.Any:
        """
        Parse value from string.

        Convert :code:`value` to

        .. code-block:: python

           >>> parser = Config()
           >>> parser.parse('12345', type_=int)
           <<< 12345
           >>>
           >>> parser.parse('1,2,3,4', type_=list, subtype=int)
           <<< [1, 2, 3, 4]

        :param value: string
        :param type\\_: the type to return
        :param subtype: subtype for iterator types
        :return: the parsed config value

        """
        if type_ is bool:
            return type_(value.lower() in self.TRUE_STRINGS)

        try:
            if isinstance(type_, type) and issubclass(
                type_, (list, tuple, set, frozenset)
            ):
                return type_(
                    self.parse(v.strip(" "), subtype)
                    for v in value.split(",")
                    if value.strip(" ")
                )

            return type_(value)
        except ValueError as e:
            raise ConfigError(*e.args)

    def get(
        self,
        key: str,
        default: typing.Any = UNSET,
        type_: typing.Type[typing.Any] = str,
        subtype: typing.Type[typing.Any] = str,
        mapper: typing.Optional[typing.Callable[[object], object]] = None,
    ) -> typing.Any:
        """
        Parse a value from an environment variable.

        .. code-block:: python

           >>> os.environ['FOO']
           <<< '12345'
           >>>
           >>> os.environ['BAR']
           <<< '1,2,3,4'
           >>>
           >>> 'BAZ' in os.environ
           <<< False
           >>>
           >>> parser = Config()
           >>> parser.get('FOO', type_=int)
           <<< 12345
           >>>
           >>> parser.get('BAR', type_=list, subtype=int)
           <<< [1, 2, 3, 4]
           >>>
           >>> parser.get('BAZ', default='abc123')
           <<< 'abc123'
           >>>
           >>> parser.get('FOO', type_=int, mapper=lambda x: x*10)
           <<< 123450

        :param key: the key to look up the value under
        :param default: default value to return when when no value is present
        :param type\\_: the type to return
        :param subtype: subtype for iterator types
        :param mapper: a function to post-process the value with
        :return: the parsed config value

        """
        value = self.environ.get(key, UNSET)

        if value is UNSET and default is UNSET:
            raise ConfigError("Unknown environment variable: {0}".format(key))

        if value is UNSET:
            value = default
        else:
            value = self.parse(typing.cast(str, value), type_, subtype)

        if mapper:
            value = mapper(value)

        return value


config = Config()
