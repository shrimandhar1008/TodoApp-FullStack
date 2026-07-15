import pytest




def test_equal_or_not_equal():
    assert 5 == 5
    assert 5 != 6

def test_is_instance():
    assert isinstance(5, int)
    assert not isinstance("hello", int)

class Student:
    def __init__(self, first_name, last_name, major, years):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.year = years


@pytest.fixture
def default_employee():
    return Student("John", "Doe", "Computer Science", 2)


def test_person_initialization(default_employee):
    student = default_employee
    assert student.first_name == "John"
    assert student.last_name == "Doe"
    assert student.major == "Computer Science"
    assert student.year == 2