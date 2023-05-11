from jadebug.connect import connect_to_jvm

def test_error():
    connection = connect_to_jvm()
    package = connection.read_package()
    print(package)
    assert False
