from jadebug.connect import connect_to_jvm

def test_error():
    connect_to_jvm()
    assert False
