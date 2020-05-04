import pytest
from contextlib import contextmanager

import cliphandler as ch
import pywintypes


@contextmanager
def does_not_raise():
    yield


def find_data(data):
    if isinstance(data, ch.Datum):
        return data.data
    elif isinstance(data, ch.Clip):
        return data.data[0].data
    elif isinstance(data, list):
        if len(data) < 1:
            return []
        else:
            return data[0]
    else:
        return data


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
            # (None, pytest.raises(TypeError), "integer is required"),
            (3, pytest.raises(ValueError), "CF_METAFILEPICT format not supported")
        ]
    )
    def test_translate_errors(self, format_, expectation, description):
        with expectation as err_info:
            ch.Format(format_)
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

    def test_eq_ne(self):
        format_str_1 = ch.Format(13)
        format_str_2 = ch.Format.from_data("text")
        assert format_str_1 == format_str_2
        assert format_str_2 == format_str_1

        format_html = ch.Format(49443)
        assert format_str_1 != format_html
        assert format_html != format_str_1

        format_delta = ch.Format(13)
        format_delta.name = "Not Unicode Text"
        assert format_str_1 == format_delta
        format_delta.id = 1
        format_delta.name = format_str_1.name
        assert format_str_1 != format_delta


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
    return find_data(add_target)


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


class TestClip:
    @pytest.fixture(params=[
        "test_single_str",
        ch.Datum("<b>Html Text</b>", 49443),
        ["str a", "str b", "str c"],
        ch.Clip(["string_1", "string_2"]),
        [[1, 2, 3], [4, 5], 6],
        ["test", 1, None, b"bytes"],
    ], ids=[
        "clip_single_str",
        "clip_single_datum_html",
        "clip_list_3str",
        "clip_from_clip_2str",
        "clip_list_lists_3int",
        "clip_list_mixd",
    ])
    def class_params(self, request):
        return request.param

    @pytest.fixture
    def my_clip(self, class_params):
        return ch.Clip(class_params)

    @pytest.fixture
    def clip_data(self, class_params):
        return find_data(class_params)

    @pytest.fixture
    def list_clip(self):
        return ch.Clip(["item 1", "item 2", "item 3", "item 4", "item 5"])

    running_ids = []

    def test_init(self, my_clip, clip_data):
        assert my_clip[0].data == clip_data
        assert my_clip.seq_num not in TestClip.running_ids
        TestClip.running_ids += [my_clip.seq_num]

    @pytest.mark.parametrize(
        "data, expectation, description",
        [
            (None, pytest.raises(IndexError), "list index out of range"),
            ([], pytest.raises(IndexError), "list index out of range")
        ],
        ids= [
            "clip_None",
            "clip_empty"
        ]
    )
    def test_init_errors(self, data, expectation, description):
        clip = ch.Clip(data)
        assert clip.seq_num < 0
        assert "Clip" in type(clip).__name__
        with expectation as err_info:
            print(clip[0].data)
        assert description in str(err_info.value)

    def test_get(self, list_clip):
        assert list_clip[0].data == "item 1"
        assert list_clip[-1].data == "item 5"
        assert [i.data for i in list_clip[0:3]] == ["item 1", "item 2", "item 3"]
        assert [i.data for i in list_clip[0:5:2]] == ["item 1", "item 3", "item 5"]
        with pytest.raises(IndexError):
            list_clip[5] += 1

    def test_set(self, list_clip):
        assert list_clip[0].data == "item 1"
        list_clip[0] = "item a"
        assert list_clip[0].data == "item a"
        assert len(list_clip) == 5
        list_clip[-1] = "item e"
        assert list_clip[4].data == "item e"
        list_clip[1:4] = ["item b", "item c", "item d"]
        assert [i.data for i in list_clip[:]] == \
               ["item a", "item b", "item c", "item d", "item e"]

    def test_del(self, list_clip):
        assert len(list_clip) == 5
        del list_clip[2]
        assert len(list_clip) == 4
        assert [i.data for i in list_clip[:]] == \
               ["item 1", "item 2", "item 4", "item 5"]
        del list_clip[1:3]
        assert [i.data for i in list_clip[:]] == ["item 1", "item 5"]

    def test_str(self, my_clip, clip_data):
        if clip_data == "<b>Html Text</b>":
            pytest.skip("Relying on HTML text detection, which is not"
                        "currently implemented.")
        assert str(my_clip.seq_num) in str(my_clip)
        assert str(len(my_clip.data)) in str(my_clip)
        assert str(ch.Datum(clip_data)) in str(my_clip)

    def test_formats(self, my_clip, clip_data):
        if clip_data == "<b>Html Text</b>":
            pytest.xfail("HTML string detection not currently implemented.")
        assert ch.Format.from_data(clip_data).name == my_clip.formats()[0].name

    def test_add(self, my_clip, clip_data, add_target, add_result):
        result_forward = my_clip + add_target
        assert "Clip" in type(result_forward).__name__
        assert result_forward[0].data == clip_data
        assert result_forward[len(my_clip)].data == add_result
        result_reverse = add_target + my_clip
        assert "Clip" in type(result_reverse).__name__
        assert result_reverse.data[0].data == add_result
        assert result_reverse.data[-len(my_clip)].data == clip_data

