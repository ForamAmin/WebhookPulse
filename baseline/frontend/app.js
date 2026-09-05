// Product catalogue — 10 items, placeholder data
const PRODUCTS = [
  {
    id: 1,
    name: "Wireless Earbuds",
    price: 1999,
    image: "https://picsum.photos/seed/earbuds/300/300",
  },
  {
    id: 2,
    name: "Cotton T-Shirt",
    price: 599,
    image: "https://picsum.photos/seed/tshirt/300/300",
  },
  {
    id: 3,
    name: "Steel Water Bottle",
    price: 449,
    image: "https://picsum.photos/seed/bottle/300/300",
  },
  {
    id: 4,
    name: "Backpack",
    price: 1799,
    image: "https://picsum.photos/seed/backpack/300/300",
  },
  {
    id: 5,
    name: "Desk Lamp",
    price: 899,
    image: "https://picsum.photos/seed/lamp/300/300",
  },
  {
    id: 6,
    name: "Notebook Set",
    price: 299,
    image: "https://picsum.photos/seed/notebook/300/300",
  },
  {
    id: 7,
    name: "Sunglasses",
    price: 749,
    image: "https://picsum.photos/seed/sunglasses/300/300",
  },
  {
    id: 8,
    name: "Bluetooth Speaker",
    price: 2499,
    image: "https://picsum.photos/seed/speaker/300/300",
  },
  {
    id: 9,
    name: "Coffee Mug",
    price: 349,
    image: "https://picsum.photos/seed/mug/300/300",
  },
  {
    id: 10,
    name: "Running Shoes",
    price: 3299,
    image: "https://picsum.photos/seed/shoes/300/300",
  },
];

// Cart state: { [productId]: quantity }
const cart = {};

const grid = document.getElementById("product-grid");
const cartCountEl = document.getElementById("cart-count");
const cartTotalEl = document.getElementById("cart-total");
const payBtn = document.getElementById("pay-btn");

// FastAPI backend
const BACKEND_URL = "http://127.0.0.1:8000";

// Format amount as Indian Rupees
function formatINR(amount) {
  return "₹" + amount.toLocaleString("en-IN");
}

// Render products
function renderProducts() {
  grid.innerHTML = "";

  PRODUCTS.forEach((product) => {
    const qty = cart[product.id] || 0;

    const card = document.createElement("div");

    card.className = "card" + (qty > 0 ? " selected" : "");

    card.innerHTML = `
      <img
        class="card-image"
        src="${product.image}"
        alt="${product.name}"
        loading="lazy"
      >

      <p class="card-name">${product.name}</p>

      <p class="card-price">
        ${formatINR(product.price)}
      </p>

      <div class="qty-row">
        <button
          class="qty-btn"
          data-action="decrease"
          data-id="${product.id}"
        >
          −
        </button>

        <span class="qty-value">${qty}</span>

        <button
          class="qty-btn"
          data-action="increase"
          data-id="${product.id}"
        >
          +
        </button>
      </div>

      <button
        class="select-btn ${qty > 0 ? "selected" : ""}"
        data-action="select"
        data-id="${product.id}"
      >
        ${qty > 0 ? "Selected" : "Select"}
      </button>
    `;

    grid.appendChild(card);
  });
}

// Update cart summary
function updateCartBar() {
  const totalItems = Object.values(cart).reduce(
    (sum, quantity) => sum + quantity,
    0
  );

  const totalAmount = PRODUCTS.reduce(
    (sum, product) =>
      sum + (cart[product.id] || 0) * product.price,
    0
  );

  cartCountEl.textContent =
    `${totalItems} item${totalItems === 1 ? "" : "s"}`;

  cartTotalEl.textContent = formatINR(totalAmount);

  payBtn.disabled = totalItems === 0;
}

// Set product quantity
function setQuantity(productId, quantity) {
  if (quantity <= 0) {
    delete cart[productId];
  } else {
    cart[productId] = quantity;
  }

  renderProducts();
  updateCartBar();
}

// Handle product buttons
grid.addEventListener("click", (event) => {
  const btn = event.target.closest("button");

  if (!btn) {
    return;
  }

  const id = Number(btn.dataset.id);
  const currentQty = cart[id] || 0;

  if (btn.dataset.action === "increase") {
    setQuantity(id, currentQty + 1);
  }

  else if (btn.dataset.action === "decrease") {
    setQuantity(id, Math.max(0, currentQty - 1));
  }

  else if (btn.dataset.action === "select") {
    setQuantity(id, currentQty > 0 ? 0 : 1);
  }
});

// Pay button
payBtn.addEventListener("click", async () => {
  const totalItems = Object.values(cart).reduce(
    (sum, quantity) => sum + quantity,
    0
  );

  const totalAmount = PRODUCTS.reduce(
    (sum, product) =>
      sum + (cart[product.id] || 0) * product.price,
    0
  );

  if (totalItems === 0) {
    return;
  }

  // Prevent multiple clicks while the request is running
  payBtn.disabled = true;
  payBtn.textContent = "Creating Payment...";

  try {
    // Send order/payment information to FastAPI
    const response = await fetch(`${BACKEND_URL}/create-payment`, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        amount: totalAmount * 100, // MockGateway expects paise, not rupees
        total_items: totalItems,
        cart: cart,
      }),
    });

    // Check whether backend responded successfully
    if (!response.ok) {
      throw new Error(
        `Backend returned ${response.status}`
      );
    }

    // Read backend response
    const data = await response.json();

    console.log("Payment created:", data);

    // Backend should return redirect_url
    if (!data.redirect_url) {
      console.error("Payment creation failed - backend response:", data);
      throw new Error(
        data.mockgateway_response
          ? JSON.stringify(data.mockgateway_response)
          : "No redirect URL received from backend"
      );
    }

    // Send the browser to MockGateway checkout page
    window.location.href = data.redirect_url;

  } catch (error) {
    console.error("Payment creation failed:", error);

    alert(
      `Unable to create payment: ${error.message}`
    );

    // Restore button
    payBtn.disabled = false;
    payBtn.textContent = "Pay";
  }
});

// Initial render
renderProducts();
updateCartBar();