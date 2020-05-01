import pytest
from contextlib import contextmanager

import cliphandler as ch
import pywintypes


@contextmanager
def does_not_raise():
    yield


class TestFormat:
    test_pairs = [
        (13, "UNICODETEXT"),
        (1, "TEXT"),
        (2, "BITMAP"),
        (49443, "HTML Format"),
        (49435, "Shell IDList Array"),
    ]

    @pytest.fixture(params=test_pairs, ids=[
        "unicodetext",
        "plaintext",
        "bitmap",
        "html text",
        "shell ID list"
    ])
    def format_pair(self, request):
        return request.param[0], request.param[1]

    @pytest.fixture
    def my_format(self, format_pair):
        return ch.Format(format_pair[0])

    def test_translate(self, format_pair):
        assert ch.Format.translate_format(format_pair[0]) == format_pair[1]

    @pytest.mark.parametrize(
        "format_, expectation, description",
        [
            (1, does_not_raise(), "None"),
            (-1, pytest.raises(pywintypes.error), "The handle is invalid"),
            (None, pytest.raises(TypeError), "integer is required")
        ]
    )
    def test_translate_errors(self, format_, expectation, description):
        with expectation as err_info:
            ch.Format.translate_format(format_)
        assert description in str(err_info)

    def test_init(self, format_pair, my_format):
        # my_format = ch.Format(format_id)
        # assert my_format.name == format_name
        assert my_format.name == format_pair[1]

    @pytest.mark.parametrize("input_data, format_id, format_name",
                             [
                                 ("test", 13, "UNICODETEXT"),
                                 (None, None, None),
                             ])
    def test_from_data(self, input_data, format_id, format_name):
        data_format = ch.Format.from_data(input_data)
        assert True
        assert data_format.id == format_id
        assert data_format.name == format_name

    def test_to_str(self, format_pair, my_format):
        assert str(format_pair[0]) in str(my_format) and \
               format_pair[1] in str(my_format)


class TestSingle:
    @pytest.fixture(params=[
        {"data": "unicodetext", "format": 13},
        {"data": "plaintext", "format": 1},
        {"data": "text unformatted", "format": None},
    ])
    def my_single(self, request):
        return ch.Single(**request.param), request.param

    def test_init(self):
        pass
