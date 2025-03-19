function searchProducts() {
    const searchQuery = document.getElementById("search").value;
    const priceRange = document.getElementById("price-range").value;
    document.getElementById("product-grid").innerHTML = "<p>Loading results...</p>";

    // Here you can integrate API calls to fetch products from Myntra, Flipkart, Amazon
    // For demonstration, we'll use a setTimeout to simulate an API call

    setTimeout(() => {
        // Simulated product data
        const products = [
            {
                name: "Product 1",
                price: "₹500",
                image: "https://via.placeholder.com/150",
                url: "#"
            },
            {
                name: "Product 2",
                price: "₹1000",
                image: "https://via.placeholder.com/150",
                url: "#"
            },
            {
                name: "Product 3",
                price: "₹1500",
                image: "https://via.placeholder.com/150",
                url: "#"
            }
        ];

        // Clear the loading message
        document.getElementById("product-grid").innerHTML = "";

        // Display the products
        products.forEach(product => {
            const productElement = document.createElement("div");
            productElement.className = "product";
            productElement.innerHTML = `
                <img src="${product.image}" alt="${product.name}">
                <h3>${product.name}</h3>
                <p class="price">${product.price}</p>
                <a href="${product.url}" class="buy-button">Buy Now</a>
            `;
            document.getElementById("product-grid").appendChild(productElement);
        });
    }, 2000); // Simulate a 2-second API call
}