from time import sleep
import pytest
from contextlib import contextmanager

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import Signal, Slot
import pytestqt  # this is being used for qapp and qtbot
import pywintypes

import cliphandler as ch
import win32clipboard as wc


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
    elif isinstance(data, QtGui.QImage):
        ba = QtCore.QByteArray()
        buffer = QtCore.QBuffer(ba)
        buffer.open(QtCore.QIODevice.WriteOnly)
        data.save(buffer, "PNG")
        return buffer.data()
    else:
        return data


class TestFormat:
    test_pairs = [
        (13, "UNICODETEXT"),
        (1, "TEXT"),
        (2, "BITMAP"),
        (49443, "HTML Format"),
        (49435, "Shell IDList Array"),
        (3, "METAFILEPICT"),
    ]

    @pytest.fixture(params=test_pairs, ids=[
        "unicodetext",
        "plaintext",
        "bitmap",
        "html_text",
        "shell_ID_list",
        "METAFILEPICT"
    ])
    def format_pair(self, request):
        return request.param[0], request.param[1]

    @pytest.fixture
    def my_format(self, format_pair):
        return ch.Format(format_pair[0])

    def test_translate(self, format_pair):
        assert ch.Format(format_pair[0]).name == format_pair[1]

    @pytest.mark.parametrize(
        "format_, expectation, description",
        [
            (1, does_not_raise(), "None"),
            (-1, pytest.raises(pywintypes.error), "The handle is invalid"),
            # (None, pytest.raises(TypeError), "integer is required"),
            # (3, pytest.raises(ValueError), "CF_METAFILEPICT format not supported")
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

    def test_to_str(self, format_pair, my_format):
        assert str(format_pair[0]) in str(my_format) and \
               format_pair[1] in str(my_format)

    def test_eq_ne(self):
        format_str_1 = ch.Format(13)
        format_str_2 = ch.Format(13)
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


add_params = [
    (ch.Datum("test_datum")),
    (["test_list"]),
    (["test_multi", "item 2", 44]),
    (ch.Clip("test_clip")),
    (ch.Clip(["test_clip_multi", 2, None, 44])),
    ("test_string"),
    (912),
    (ch.Datum(None, 3))
]

add_ids=[
    "add_datum",
    "add_list_single",
    "add_list_many",
    "add_clip_single",
    "add_clip_many",
    "add_string",
    "add_int",
    "add_metafilepict_None"
]


class TestDatum:
    big_text = "testtext"*40

    @pytest.fixture(params=[
        {"data": "unicodetext", "format_": 13},
        {"data": "plaintext", "format_": 1},
        {"data": "text unformatted", "format_": None},
        {"data": big_text, "format_": None},
        {"data": b"METAFILEPICT", "format_": 3},
        {"data": QtGui.QImage("punched.png"), "format_": 49927},
    ], ids=[
        "datum_unicode_text",
        "datum_plaintext",
        "datum_unformatted_text",
        "datum_big_text",
        "datum_metafilepict",
        "datum_qimage"
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
            return ch.Datum(class_params["data"]).format

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
        assert my_datum.data == find_data(class_params["data"])
        assert my_datum.format == response_format
        assert type(my_datum.data) == type(find_data(class_params["data"]))

    def test_str(self, class_params, my_datum, response_format):
        assert response_format.name in str(my_datum)
        assert str(find_data(class_params["data"]))[0:40] in str(my_datum)

    @pytest.mark.parametrize("addend", add_params, ids=add_ids)
    def test_add(self, my_datum, addend):
        result_forward = my_datum + addend
        assert "Clip" in type(result_forward).__name__
        assert result_forward.data[0].data == my_datum.data
        assert result_forward.data[1].data == find_data(addend)
        result_reverse = addend + my_datum
        assert "Clip" in type(result_reverse).__name__
        assert result_reverse.data[0].data == find_data(addend)
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


@pytest.fixture(params=[
    "test_single_str",
    ch.Datum("<b>Html Text</b>", 49443),
    ["str a", "str b", "str c"],
    ch.Clip(["string_1", "string_2"]),
    [[1, 2, 3], [4, 5], 6],
    ["test", 1, None, b"bytes"],
    QtGui.QImage("punched.png")
], ids=[
    "clip_single_str",
    "clip_single_datum_html",
    "clip_list_3str",
    "clip_from_clip_2str",
    "clip_list_lists_3int",
    "clip_list_mixed",
    "clip_png_qimage",
])
def clip_params(request):
    return request.param


@pytest.fixture
def clip_data(clip_params):
    return find_data(clip_params)


class TestClip:
    @pytest.fixture
    def my_clip(self, clip_params):
        return ch.Clip(clip_params)

    @pytest.fixture
    def list_clip(self):
        return ch.Clip(["item 1", "item 2", "item 3", "item 4", "item 5"])

    running_ids = []

    def test_init(self, my_clip, clip_data):
        assert my_clip[0].data == clip_data
        assert my_clip.seq_num not in TestClip.running_ids
        TestClip.running_ids += [my_clip.seq_num]

    # @pytest.mark.parametrize(
    #     "data, expectation, description",
    #     [
    #         (None, pytest.raises(IndexError), "list index out of range"),
    #         ([], pytest.raises(IndexError), "list index out of range")
    #     ],
    #     ids= [
    #         "clip_None",
    #         "clip_empty"
    #     ]
    # )
    # def test_init_errors(self, data, expectation, description):
    #     clip = ch.Clip(data)
    #     assert clip.seq_num < 0
    #     assert "Clip" in type(clip).__name__
    #     with expectation as err_info:
    #         print(clip[0].data)
    #     assert description in str(err_info.value)
    @pytest.mark.parametrize(
        "data",
        [
            None,
            []
        ],
        ids= [
            "clip_None",
            "clip_empty"
        ]
    )
    def test_init_errors(self, data):
        clip = ch.Clip(data)
        assert clip[0].data is None

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
        assert str(clip_data)[:40] in str(my_clip)

    def test_formats(self, my_clip, clip_data, clip_params):
        if clip_data == "<b>Html Text</b>":
            pytest.xfail("HTML string detection not currently implemented.")
        assert ch.Datum(clip_params).format.name == my_clip.formats()[0].name

    @pytest.fixture
    def multiple_format_clip(self):
        many_formats = [1, 2, 4, 6, 13]
        datums = [ch.Datum(f"datum {x}") for x in range(0, len(many_formats))]
        for idx, format_ in enumerate(many_formats):
            datums[idx].format = ch.Format(format_)
        return ch.Clip(datums)

    @pytest.mark.parametrize("formats, expected", [
        (1, 1),
        ([1, 2], 1),
        ([2, 1], 2),
        ([3, 1, 2], 1),
        ([14, 19, 13, 1], 13),
    ])
    def test_priority_order(self, multiple_format_clip, formats, expected):
        assert multiple_format_clip.find(formats).format.id == expected

    @pytest.mark.parametrize("addend", add_params, ids=add_ids)
    def test_add(self, my_clip, clip_data, addend):
        result_forward = my_clip + addend
        assert "Clip" in type(result_forward).__name__
        assert result_forward[0].data == clip_data
        assert result_forward[len(my_clip)].data == find_data(addend)
        result_reverse = addend + my_clip
        assert "Clip" in type(result_reverse).__name__
        assert result_reverse.data[0].data == find_data(addend)
        assert result_reverse.data[-len(my_clip)].data == clip_data

    def test_for(self):
        array = [1, 2, 3, 4]
        array_clip = ch.Clip(array)
        for a, b in zip(array_clip, array):
            assert a.data == b


# def qimage_from_clip_bitmap(clip):
#     byte_str = clip.find(XYZZY):
#     byte_array = QtCore.QByteArray(clip.find(XYZZY))
#     q_image = QImage.fromData(byte_array)
#     return q_image

@pytest.fixture(params=[
    None,
    QtGui.QImage("punched.png"),
    "test string a",
], ids=[
    "cb_empty",
    "cb_image",
    "cb_string",
    # "cb_self_html_text",
    # TODO: "cb_self_image"
])
def load_params(request):
    return request.param


@pytest.fixture
def load_qclipboard(load_params, qapp):
    q_clipboard = qapp.clipboard()
    if load_params is None:
        q_clipboard.clear()
    elif isinstance(load_params, QtGui.QImage):
        q_clipboard.setImage(load_params)
    elif isinstance(load_params, str):
        q_clipboard.setText(load_params)
    else:
        raise ValueError("Don't know how to load that datatype into the clipboard!")


@pytest.fixture
def read_qclipboard(load_params, qapp):
    q_clipboard = qapp.clipboard()

    def _read_qclipboard():
        if isinstance(load_params, QtGui.QImage):
            return q_clipboard.image()
        else:
            if q_clipboard.text() == "":
                return None
            return q_clipboard.text()

    return _read_qclipboard


@pytest.fixture
def clear_qclipboard(qapp):
    q_clipboard = qapp.clipboard()
    q_clipboard.clear()


class TestHandler:
    @pytest.fixture
    def my_handler(self):
        with ch.Handler() as handler:
            yield handler

    @pytest.mark.usefixtures("load_qclipboard")
    def test_read(self, my_handler, load_params):
        clip = my_handler.read()
        assert find_data(load_params) == clip.find(ch.Datum(load_params).format.id).data

    @pytest.mark.usefixtures("clear_qclipboard")
    def test_write(self, read_qclipboard, load_params):
        clip = ch.Clip(load_params)
        with ch.Handler() as my_handler:
            my_handler.write(clip)
        assert read_qclipboard() == load_params

    @pytest.mark.usefixtures("load_qclipboard")
    def test_clear(self, read_qclipboard, load_params, qapp):
        assert read_qclipboard() == load_params
        with ch.Handler() as my_handler:
            my_handler.clear()
        assert qapp.clipboard().text() is ""

    @pytest.mark.usefixtures("load_qclipboard")
    def test_seq(self, my_handler, load_params):
        current_seq = my_handler.seq()
        assert current_seq > 0
        my_handler.write(ch.Clip(load_params))
        assert my_handler.current_seq > current_seq

    def test_seq_2(self, my_handler):
        current_seq = my_handler.seq()
        my_handler.clear()
        assert my_handler.current_seq == current_seq + 1
        my_handler.write(ch.Clip("test"))
        assert my_handler.current_seq == current_seq + 3

    def test_mutexes(self, qapp):
        handler_1 = ch.Handler()
        assert ch.cb_mutex.try_lock() is True
        ch.cb_mutex.unlock()
        handler_1.__enter__()
        assert ch.cb_mutex.try_lock() is False
        handler_1.write("test mutex")
        handler_1.__exit__()
        assert ch.cb_mutex.try_lock() is True
        ch.cb_mutex.unlock()
        with handler_1:
            new_clip = handler_1.read()
        assert new_clip[0].data == "test mutex"


class SampleSignals(QtCore.QObject):
    start_monitor = Signal()
    load_data = Signal(ch.Clip)
    send_exit = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)


class TestMonitor:
    @pytest.fixture(scope="class", autouse=True)
    def temp_signals(self, qapp):
        return SampleSignals(qapp)

    @pytest.fixture(scope="class", autouse=True)
    def monitor_thread(self, qapp):
        new_thread = QtCore.QThread()
        return new_thread

    @pytest.fixture(scope="class", autouse=True)
    def my_monitor(self, temp_signals, monitor_thread, qapp):
        monitor = ch.Monitor()
        monitor.moveToThread(monitor_thread)
        temp_signals.start_monitor.connect(monitor.begin)
        temp_signals.load_data.connect(monitor.load)
        temp_signals.send_exit.connect(monitor.end)
        monitor_thread.start()
        temp_signals.start_monitor.emit()
        sleep(0.01)
        return monitor

    @staticmethod
    def mutex_please():
        try_count = 0
        while try_count < 50:
            if ch.cb_mutex.tryLock(10):
                return True
            try_count += 1
        return False

    def test_thread_init(self, my_monitor, monitor_thread):
        assert monitor_thread.isRunning()
        assert my_monitor.timer.isActive()

    def test_mutex(self, my_monitor):
        assert self.mutex_please()
        ch.cb_mutex.unlock()
        sleep(0.2)
        assert my_monitor.try_count < 1
        assert self.mutex_please()
        sleep(0.5)
        assert my_monitor.try_count >= 40
        ch.cb_mutex.unlock()
        sleep(0.2)
        assert my_monitor.try_count < 1

    def test_signals(self, my_monitor, load_params, qtbot):
        with qtbot.waitSignals([(my_monitor.clipboard_updated, "clipboard updated"),
                                (my_monitor.new_card_from_clipboard, "new card recieved")],
                               timeout=2000, order="strict"):
            with ch.Handler() as my_handler:
                my_handler.write(load_params)

    def test_catch_clip(self, my_monitor, load_params, qtbot):
        with qtbot.waitSignal(my_monitor.new_card_from_clipboard,
                              timeout=2000) as new_signal:
            with ch.Handler() as my_handler:
                my_handler.write(load_params)
        assert new_signal.args[0][0].data == find_data(load_params)

    def test_load(self, my_monitor, load_params, temp_signals, qtbot):
        with qtbot.assertNotEmitted(my_monitor.new_card_from_clipboard):
            temp_handler = ch.Handler()
            with temp_handler:
                temp_handler.clear()
            temp_signals.load_data.emit(ch.Clip(load_params))
            sleep(0.1)
            with temp_handler:
                data_a = temp_handler.read()[0].data
                data_b = find_data(load_params)
                assert data_a == data_b
                # assert temp_handler.read()[0].data == find_data(load_params)

    def test_exit(self, my_monitor, monitor_thread, temp_signals):
        assert not monitor_thread.isFinished()
        temp_signals.send_exit.emit()
        sleep(0.5)
        assert my_monitor.timer.isActive() is False
        monitor_thread.quit()
        monitor_thread.wait()
        sleep(0.5)
        assert monitor_thread.isFinished()