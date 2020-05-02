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
        "html_text",
        "shell_ID_list"
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


@pytest.fixture(params=[
    (ch.Datum("test_datum")),
    (["test_list"]),
    (["test_multi", "item 2", 44]),
    (ch.Clip("test_clip")),
    (ch.Clip(["test_clip_multi", 2, None, 44])),
    ("test_string"),
    (912),
], ids=[
    "add_datum",
    "add_list_single",
    "add_list_many",
    "add_clip_single",
    "add_clip_many",
    "add_string",
    "add_int",
])
def add_target(request):
    return request.param


@pytest.fixture
def add_result(add_target):
    if isinstance(add_target, ch.Datum):
        return add_target.data
    elif isinstance(add_target, ch.Clip):
        return add_target.data[0].data
    elif isinstance(add_target, list):
        return add_target[0]
    else:
        return add_target


class TestDatum:
    big_text = "testtext"*40

    @pytest.fixture(params=[
        {"data": "unicodetext", "format_": 13},
        {"data": "plaintext", "format_": 1},
        {"data": "text unformatted", "format_": None},
        {"data": big_text, "format_": None},
    ], ids=[
        "datum_unicode_text",
        "datum_plaintext",
        "datum_unformatted_text",
        "datum_big_text"
    ])
    def class_params(self, request):
        return request.param
    
    @pytest.fixture
    def my_datum(self, class_params):
        return ch.Datum(**class_params)

    @pytest.fixture
    def response_format(self, class_params):
        if class_params["format_"]:
            return ch.Format(class_params["format_"])
        else:
            return ch.Format.from_data(class_params["data"])

    # @pytest.fixture
    # def expected_execptions(self, class_params):
    #     disambiguate = {
    #         "NoneType": "None invalid exception hey kayla"
    #     }
    #     param_type = type(class_params).__name__
    #     if param_type in disambiguate:
    #         return disambiguate[param_type]
    #     else:
    #         return does_not_raise()

    def test_init(self, class_params, my_datum, response_format):
        assert my_datum.data == class_params["data"]
        assert my_datum.format == response_format
        assert type(my_datum.data) == type(class_params["data"])

    def test_str(self, class_params, my_datum, response_format):
        assert class_params["data"][0:40] in str(my_datum)
        assert str(response_format) in str(my_datum)

    def test_add(self, my_datum, add_target, add_result):
        result_forward = my_datum + add_target
        assert "Clip" in type(result_forward).__name__
        assert result_forward.data[0].data == my_datum.data
        assert result_forward.data[1].data == add_result
        result_reverse = add_target + my_datum
        assert "Clip" in type(result_reverse).__name__
        assert result_reverse.data[0].data == add_result
        assert result_reverse.data[-1].data == my_datum.data

    def test_add_none(self, my_datum):
        result_forward = my_datum + None
        assert "Clip" in type(result_forward).__name__
        assert result_forward.data[0].data == my_datum.data
        assert len(result_forward.data) == 1
        result_reverse = None + my_datum
        assert "Clip" in type(result_reverse).__name__
        assert result_reverse.data[0].data == my_datum.data
        assert len(result_forward.data) == 1