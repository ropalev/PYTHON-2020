def get_words(text):
    return text.split()

def test_splot():
    text = "one or another"
    expected_words = ["one", "or", "another"]
    words = get_words(text)
    assert  expected_words == words