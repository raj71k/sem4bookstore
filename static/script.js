// Check if the event listeners have already been added
if (!document.cartListenersAdded) {
    document.addEventListener('DOMContentLoaded', function () {
        const addToCartButtons = document.querySelectorAll('.addToCart');
        const viewCartButton = document.querySelector('.cart-container .btn-success');
        const cart = {};

        addToCartButtons.forEach(button => {
            button.addEventListener('click', function () {
                const bookName = this.getAttribute('data-book');
                const bookPrice = parseFloat(this.getAttribute('data-price'));
                if (cart[bookName]) {
                    cart[bookName].quantity++;
                } else {
                    cart[bookName] = { quantity: 1, price: bookPrice };
                }
                console.log('Cart Updated:', cart); // Log the updated cart
                updateCartCount();
            });
        });

        viewCartButton.addEventListener('click', function () {
            console.log('View Cart Clicked');
            const cartJson = encodeURIComponent(JSON.stringify(cart));
            window.location.href = '/order?cart=' + cartJson;
        });

        function updateCartCount() {
            // Calculate the total quantity from the cart data
            const totalQuantity = Object.values(cart).reduce((acc, val) => {
                if (val && typeof val === 'object' && val.quantity) {
                    return acc + val.quantity;
                } else if (typeof val === 'number') {
                    return acc + val;
                }
                return acc;
            }, 0);

            // Update the cart count display (you can customize this part based on your UI)
            viewCartButton.innerHTML = `View Cart (${totalQuantity})`;
        }

        // Set flag indicating that event listeners have been added
        document.cartListenersAdded = true;
    });
}