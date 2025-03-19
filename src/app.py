from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from scraper.scraper import Scraper
from api.api_handler import APIHandler
from utils.data_processing import filter_by_price_range, consolidate_data
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor
import asyncio

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

scraper = Scraper()
api_handler = APIHandler()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('search'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('signup'))
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('search'))
        
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def fetch_source_data(scraper, product_name, source):
    try:
        products = scraper.fetch_product_data(product_name, source)
        print(f"Found {len(products)} products from {source}")
        return products
    except Exception as e:
        print(f"{source} scraping failed: {e}")
        return []

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    query = request.args.get('query') or request.form.get('product_name')
    
    if query:
        try:
            print(f"Searching for: {query}")
            
            # Initialize scraper if not already initialized
            if not hasattr(app, 'scraper'):
                app.scraper = Scraper()
            
            # Fetch results with error handling for each source
            results = {}
            
            try:
                flipkart_results = app.scraper.fetch_flipkart_data(query)
                results['flipkart'] = flipkart_results
                print(f"Flipkart results: {len(flipkart_results)} products found")
            except Exception as e:
                print(f"Flipkart error: {e}")
                results['flipkart'] = []

            try:
                amazon_results = app.scraper.fetch_amazon_data(query)
                results['amazon'] = amazon_results
                print(f"Amazon results: {len(amazon_results)} products found")
            except Exception as e:
                print(f"Amazon error: {e}")
                results['amazon'] = []

            try:
                myntra_results = app.scraper.fetch_myntra_data(query)
                results['myntra'] = myntra_results
                print(f"Myntra results: {len(myntra_results)} products found")
            except Exception as e:
                print(f"Myntra error: {e}")
                results['myntra'] = []

            # Check if we have any results
            has_results = any(len(products) > 0 for products in results.values())
            
            if not has_results:
                flash('No products found. Please try a different search term.', 'info')
                return render_template('search.html')
                
            return render_template('results.html', results=results, query=query)
            
        except Exception as e:
            print(f"Search error: {e}")
            flash('An error occurred while searching. Please try again.', 'error')
            return render_template('search.html')
    
    return render_template('search.html')

@app.route('/reauthenticate', methods=['GET', 'POST'])
@login_required
def reauthenticate():
    if request.method == 'POST':
        password = request.form['password']
        user = current_user

        if check_password_hash(user.password, password):
            # Reauthentication successful, redirect to the desired page
            return redirect(url_for('search'))

        return render_template('reauthenticate.html', error="Invalid password")

    return render_template('reauthenticate.html')

@app.route('/wishlist', methods=['GET', 'POST'])
@login_required
def wishlist():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        # Add to wishlist logic
        return jsonify({'success': True})
    return render_template('wishlist.html', wishlist_items=current_user.wishlist)

@app.route('/price-alerts', methods=['GET', 'POST'])
@login_required
def price_alerts():
    if request.method == 'POST':
        product_url = request.form.get('product_url')
        target_price = request.form.get('target_price')
        # Set price alert logic
        return jsonify({'success': True})
    return render_template('price_alerts.html', alerts=current_user.price_alerts)

@app.route('/price-history/<product_id>')
@login_required
def price_history(product_id):
    # Get price history logic
    return render_template('price_history.html', history=price_history_data)

@app.route('/compare/<product_id>')
@login_required
def compare_products(product_id):
    # Product comparison logic
    return render_template('compare.html', comparison_data=comparison_data)

@app.route('/deals')
@login_required
def deals():
    deals = scraper.fetch_latest_deals()
    return render_template('deals.html', deals=deals)

@app.route('/home')
@login_required
def home():
    # Fetch popular products from different sources
    popular_products = scraper.fetch_latest_deals()
    return render_template('home.html', popular_products=popular_products)

@app.route('/api/search')
@login_required
def api_search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({
            'amazon': [],
            'flipkart': [],
            'myntra': []
        })

    results = {
        'amazon': scraper.fetch_product_data(query, 'amazon'),
        'flipkart': scraper.fetch_product_data(query, 'flipkart'),
        'myntra': scraper.fetch_product_data(query, 'myntra')
    }

    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create a test user if it doesn't exist
        if not User.query.filter_by(username='test').first():
            test_user = User(
                username='test',
                password=generate_password_hash('test123')
            )
            db.session.add(test_user)
            db.session.commit()
    print("Starting Flask server...")
    app.run(debug=True)
