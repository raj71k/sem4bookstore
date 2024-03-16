document.addEventListener('DOMContentLoaded', function () {
    const cartContainer = document.querySelector('.cart-container');
    const cart = {};

    cartContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('addToCart')) {
            const button = event.target;
            const bookName = button.getAttribute('data-book');
            const bookPrice = parseFloat(button.getAttribute('data-price'));

            if (cart[bookName]) {
                cart[bookName].quantity++;
            } else {
                cart[bookName] = { quantity: 1, price: bookPrice };
            }

            console.log('Cart Updated:', cart); // Log the updated cart
            updateCartCount();
        } else if (event.target.classList.contains('btn-success')) {
            console.log('View Cart Clicked');
            const cartJson = encodeURIComponent(JSON.stringify(cart));
            window.location.href = '/order?cart=' + cartJson;
        }
    });

    function updateCartCount() {
        // Calculate the total quantity and subtotal from the cart data
        let totalQuantity = 0;
        let subtotal = 0;
        for (const item in cart) {
            if (cart.hasOwnProperty(item)) {
                totalQuantity += cart[item].quantity;
                subtotal += cart[item].quantity * cart[item].price;
            }
        }

        // Update the cart count display
        const viewCartButton = document.querySelector('.cart-container .btn-success');
        viewCartButton.innerHTML = `View Cart (${totalQuantity})`;

        // Update the subtotal display
        const subtotalElement = document.getElementById('subtotal');
        if (subtotalElement) {
            subtotalElement.textContent = `Subtotal: $${subtotal.toFixed(2)}`;
        }
    }
});
