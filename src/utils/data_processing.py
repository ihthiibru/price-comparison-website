def filter_by_price_range(products, price_range):
    """
    Filters the products by the given price range in INR.
    """
    if not price_range or '-' not in price_range:
        return products  # Return all products if no valid price range is given

    try:
        min_price, max_price = map(float, price_range.split('-'))
    except ValueError:
        return products  # Return all products if conversion fails

    filtered_products = []

    for product in products:
        price = product.get('price', 0)  # Default to 0 if price is missing
        currency = product.get('currency', 'INR')  # Default to INR if missing

        try:
            price_in_inr = convert_to_inr(price, currency)
            if min_price <= price_in_inr <= max_price:
                product['price'] = price_in_inr
                product['currency'] = 'INR'
                filtered_products.append(product)
        except Exception as e:
            print(f"Error converting price: {e}")

    return filtered_products

def convert_to_inr(price, currency):
    """
    Converts the given price to INR based on the currency.
    """
    conversion_rates = {
        'USD': 74.0,  # Example conversion rate
        'EUR': 88.0,  # Example conversion rate
    }

    try:
        return price * conversion_rates.get(currency, 1)  # Default multiplier = 1 for INR
    except TypeError:
        print(f"Invalid price: {price} for currency: {currency}")
        return price  # Return original price if there's an issue

def consolidate_data(scraped_data, api_data):
    """
    Merges the scraped data and API data into a single list.
    """
    return scraped_data + api_data if scraped_data and api_data else scraped_data or api_data