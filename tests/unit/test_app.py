def test_index_page(test_client):
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'Flask Stock Portfolio App' in response.data
    assert b'Welcome to the' in response.data
    assert b'Flask Stock Portfolio App!' in response.data


def test_about_page(test_client):
    """
    GIVEN a Flask application
    WHEN the '/about' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/users/about')
    assert response.status_code == 200
    assert b'Flask Stock Portfolio App' in response.data
    assert b'About' in response.data
    assert b'This application is built using the Flask web framework.' in response.data
    # assert b'My First App' in response.data
