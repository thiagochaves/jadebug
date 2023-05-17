from jadebug.connect import connect_to_jvm
import jadebug.packages as packages
from jadebug.event import EventKind
from jadebug.header import Reply


def test_quick_start_resume_death():
    connection = connect_to_jvm()
    package = connection.read_package()
    assert package.events[0].kind == EventKind.VM_START
    command = packages.ResumeCommand()
    connection.send_command(command)
    package = connection.read_package()
    assert isinstance(package, Reply)
    package = connection.read_package()
    assert package.events[0].kind == EventKind.VM_DEATH
