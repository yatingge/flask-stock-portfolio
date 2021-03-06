from werkzeug.wrappers import response
from app import app
import requests

class MockSuccessResponse(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url
        self.headers = {'blaa': '1234'}

    def json(self):
        return {
            'Meta Data': {
                "2. Symbol": "MSFT",
                "3. Last Refreshed": "2021-11-19"
            },
            'Time Series (Daily)': {
                "2021-11-19": {
                    "4. close": "343.11",
                },
                "2021-11-18": {
                    "4. close": "341.27",
                }
            }
        }

def test_monkeypatch_get_success(monkeypatch):
    """
    GIVEN a Flask application and a monkeypatched version of requests.get()
    WHEN the HTTP response is set to successful
    THEN check the HTTP response
    """
    def mock_get(url):
        return MockSuccessResponse(url)

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', mock_get)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.url == url
    assert 'MSFT' in r.json()['Meta Data']['2. Symbol']
    assert '2021-11-19' in r.json()['Meta Data']['3. Last Refreshed']
    assert '343.11' in r.json()['Time Series (Daily)']['2021-11-19']['4. close']

def test_get_add_stock_page(test_client, log_in_default_user):
    """
    GIVEN a Flask application
    WHEN the '/add_stock' page is requested(GET)
    THEN check the response is valid
    """
    response = test_client.get('/add_stock')
    assert response.status_code == 200
    assert b'Flask Stock Portfolio App' in response.data
    assert b'Add a Stock' in response.data
    assert b'Stock Symbol <em>(required)</em>' in response.data
    assert b'Number of Shares <em>(required)</em>' in response.data
    assert b'Purchase Price ($) <em>(required)</em>' in response.data
    assert b'Purchase Date' in response.data  # NEW!

def test_get_add_stock_page_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/add_stock' page is requested (GET) when the user is not logged in
    THEN check that the user is redirected to the login page
    """
    response = test_client.get('/add_stock', follow_redirects=True)
    assert response.status_code == 200
    assert b'Add a Stock' not in response.data
    assert b'Please log in to access this page.' in response.data

def test_post_add_stock_page(test_client, log_in_default_user):
    """
    GIVEN a Flask application
    WHEN the '/add_stock' page is posted to (POST)
    THEN check that the user is redirected to the '/list_stocks' page
    """

    response = test_client.post('/add_stock',
                            data={'stock_symbol': 'AAPL',
                                    'number_of_shares': '23',
                                    'purchase_price': '432.17',
                                     'purchase_date': '2020-07-24'},
                            follow_redirects=True)
    assert response.status_code == 200
    assert b'List of Stocks' in response.data
    assert b'Stock Symbol' in response.data
    assert b'Number of Shares' in response.data
    assert b'Purchase Price' in response.data
    assert b'AAPL' in response.data
    assert b'23' in response.data
    assert b'432.17' in response.data
    assert b'Added new stock (AAPL)!' in response.data  

def test_post_add_stock_page_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/add_stock' page is posted to (POST) when the user is not logged in
    THEN check that the user is redirected to the login page
    """
    response = test_client.post('/add_stock',
                                data={'stock_symbol': 'AAPL',
                                      'number_of_shares': '23',
                                      'purchase_price': '432.17',
                                      'purchase_date': '2020-07-24'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'List of Stocks' not in response.data
    assert b'Added new stock (AAPL)!' not in response.data
    assert b'Please log in to access this page.' in response.data

def test_get_stock_list_logged_in(test_client, add_stocks_for_default_user, mock_requests_get_success_daily):
    """
    GIVEN a Flask application configured for testing, with the default user logged in
          and the default set of stocks in the database
    WHEN the '/stocks' page is requested (GET)
    THEN check the response is valid and each default stock is displayed
    """
    headers = [b'Stock Symbol', b'Number of Shares', b'Share Price', b'Purchase Date', b'Current Share Price',
               b'Stock Position Value', b'TOTAL VALUE'] 
    data = [b'SAM', b'27', b'301.23', b'2020-07-01',
            b'COST', b'76', b'14.67', b'2019-05-26',
            b'TWTR', b'146', b'34.56', b'2020-02-03']

    response = test_client.get('/stocks', follow_redirects=True)
    assert response.status_code == 200
    assert b'List of Stocks' in response.data
    for header in headers:
        assert header in response.data
    for element in data:
        assert element in response.data

def test_get_stock_list_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/stocks' page is requested (GET) when the user is not logged in
    THEN check that the user is redirected to the login page
    """
    response = test_client.get('/stocks', follow_redirects=True)
    assert response.status_code == 200
    assert b'List of Stocks' not in response.data
    assert b'Please log in to access this page.' in response.data