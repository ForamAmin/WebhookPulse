// Product catalogue — 10 items, placeholder data
const PRODUCTS = [
  { id: 1, name: "Wireless Earbuds", price: 1999, image: "https://picsum.photos/seed/earbuds/300/300" },
  { id: 2, name: "Cotton T-Shirt", price: 599, image: "https://picsum.photos/seed/tshirt/300/300" },
  { id: 3, name: "Steel Water Bottle", price: 449, image: "https://picsum.photos/seed/bottle/300/300" },
  { id: 4, name: "Backpack", price: 1799, image: "https://picsum.photos/seed/backpack/300/300" },
  { id: 5, name: "Desk Lamp", price: 899, image: "https://picsum.photos/seed/lamp/300/300" },
  { id: 6, name: "Notebook Set", price: 299, image: "https://picsum.photos/seed/notebook/300/300" },
  { id: 7, name: "Sunglasses", price: 749, image: "https://picsum.photos/seed/sunglasses/300/300" },
  { id: 8, name: "Bluetooth Speaker", price: 2499, image: "https://picsum.photos/seed/speaker/300/300" },
  { id: 9, name: "Coffee Mug", price: 349, image: "https://picsum.photos/seed/mug/300/300" },
  { id: 10, name: "Running Shoes", price: 3299, image: "https://picsum.photos/seed/shoes/300/300" },
];

// cart state: { [productId]: quantity }
const cart = {};

const grid = document.getElementById("product-grid");
const cartCountEl = document.getElementById("cart-count");
const cartTotalEl = document.getElementById("cart-total");
const payBtn = document.getElementById("pay-btn");

function formatINR(amount) {
  return "₹" + amount.toLocaleString("en-IN");
}

function renderProducts() {
  grid.innerHTML = "";

  PRODUCTS.forEach((product) => {
    const qty = cart[product.id] || 0;

    const card = document.createElement("div");
    card.className = "card" + (qty > 0 ? " selected" : "");

    card.innerHTML = `
      <img class="card-image" src="${product.image}" alt="${product.name}" loading="lazy">
      <p class="card-name">${product.name}</p>
      <p class="card-price">${formatINR(product.price)}</p>
      <div class="qty-row">
        <button class="qty-btn" data-action="decrease" data-id="${product.id}">−</button>
        <span class="qty-value">${qty}</span>
        <button class="qty-btn" data-action="increase" data-id="${product.id}">+</button>
      </div>
      <button class="select-btn ${qty > 0 ? "selected" : ""}" data-action="select" data-id="${product.id}">
        ${qty > 0 ? "Selected" : "Select"}
      </button>
    `;

    grid.appendChild(card);
  });
}

function updateCartBar() {
  const totalItems = Object.values(cart).reduce((sum, q) => sum + q, 0);
  const totalAmount = PRODUCTS.reduce((sum, p) => sum + (cart[p.id] || 0) * p.price, 0);

  cartCountEl.textContent = `${totalItems} item${totalItems === 1 ? "" : "s"}`;
  cartTotalEl.textContent = formatINR(totalAmount);
  payBtn.disabled = totalItems === 0;
}

function setQuantity(productId, qty) {
  if (qty <= 0) {
    delete cart[productId];
  } else {
    cart[productId] = qty;
  }
  renderProducts();
  updateCartBar();
}

grid.addEventListener("click", (event) => {
  const btn = event.target.closest("button");
  if (!btn) return;

  const id = Number(btn.dataset.id);
  const currentQty = cart[id] || 0;

  if (btn.dataset.action === "increase") {
    setQuantity(id, currentQty + 1);
  } else if (btn.dataset.action === "decrease") {
    setQuantity(id, Math.max(0, currentQty - 1));
  } else if (btn.dataset.action === "select") {
    setQuantity(id, currentQty > 0 ? 0 : 1);
  }
});

payBtn.addEventListener("click", () => {
  // Placeholder: this is where the frontend will call the FastAPI backend
  // to initiate a payment via MockGateway. No backend wired up yet.
  const totalItems = Object.values(cart).reduce((sum, q) => sum + q, 0);
  const totalAmount = PRODUCTS.reduce((sum, p) => sum + (cart[p.id] || 0) * p.price, 0);
  console.log("Proceeding to pay:", { totalItems, totalAmount, cart });
  alert(`Proceeding to pay ${formatINR(totalAmount)} for ${totalItems} item(s). (Backend not connected yet.)`);
});

renderProducts();
updateCartBar();