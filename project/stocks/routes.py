
from . import stocks_blueprint
from flask import current_app, render_template, request, session, flash, redirect, url_for
from project import database
from project.models import Stock
import click
from flask_login import login_required, current_user
from datetime import datetime

# @stocks_blueprint.cli.command('create_default_set')
# def create_default_set():
#     """Create three new stocks and add them to the database"""
#     stock1 = Stock('HD', '25', '247.29')
#     stock2 = Stock('TWTR', '230', '31.89')
#     stock3 = Stock('DIS', '65', '118.77')
#     database.session.add(stock1)
#     database.session.add(stock2)
#     database.session.add(stock3)
#     database.session.commit()

@stocks_blueprint.cli.command('create')
@click.argument('symbol')
@click.argument('number_of_shares')
@click.argument('purchase_price')
def create(symbol, number_of_shares, purchase_price):
    """Create a new stock and add it to the database"""
    stock = Stock(symbol, number_of_shares, purchase_price)
    database.session.add(stock)
    database.session.commit()

@stocks_blueprint.route('/')
def index():
    current_app.logger.info('Calling the index() function.')
    return render_template('stocks/index.html')

@stocks_blueprint.route('/add_stock', methods=['GET', 'POST'])
@login_required
def add_stock():
    if request.method == 'POST':
        # Save the form data to the database
        new_stock = Stock(request.form['stock_symbol'],
                          request.form['number_of_shares'],
                          request.form['purchase_price'],
                          current_user.id,
                          datetime.fromisoformat(request.form['purchase_date']))
        database.session.add(new_stock)
        database.session.commit()

        flash(f"Added new stock ({ request.form['stock_symbol'] })!", 'success')
        current_app.logger.info(f"Added new stock ({ request.form['stock_symbol'] })!")
        return redirect(url_for('stocks.list_stocks'))

    return render_template('stocks/add_stock.html')

@stocks_blueprint.route('/stocks')
@login_required
def list_stocks():
    stocks = Stock.query.order_by(Stock.id).filter_by(user_id=current_user.id).all()

    current_account_value = 0.0
    for stock in stocks:
        stock.get_stock_data()
        database.session.add(stock)
        current_account_value += stock.get_stock_position_value()

    database.session.commit()
    return render_template('stocks/stocks.html', stocks=stocks, value=round(current_account_value, 2))

@stocks_blueprint.before_request
def stocks_before_request():
    current_app.logger.info('Calling before_request() for the stocks blueprint...')


@stocks_blueprint.after_request
def stocks_after_request(response):
    current_app.logger.info('Calling after_request() for the stocks blueprint...')
    return response


@stocks_blueprint.teardown_request
def stocks_teardown_request(error=None):
    current_app.logger.info('Calling teardown_request() for the stocks blueprint...')


@stocks_blueprint.route("/chartjs_demo1")
def chartjs_demo1():
    return render_template('stocks/chartjs_demo1.html')