from matmeta.payload_metaclass import Human

def test_construct_human():
    someone = Human("Steve", "Holt", email="yeah@cool.com", institution="TV")
    assert someone.given_name == "Steve"
    assert someone["given_name"] == "Steve"
    assert someone.institution == "TV"
