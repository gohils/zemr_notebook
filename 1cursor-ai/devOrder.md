# Project Development Order

### **Step 1: Project Structure Setup**

- provide complete project structure based on the prd.md file

### **Step 2: User Authentication**

- Implement **user authentication** using **NextAuth.js** with JWT.
- Create **sign-up** and **login** pages.
- Set up **Auth Context** for global state management.
- Add **role-based access** (Admin vs. Customer) for access control.

---

### **Step 3: Admin Dashboard for Product Management**

- Implement an **Admin Dashboard** with CRUD operations for managing products.
- Add **product filtering** (by category, price, etc.) and **pagination**.
- Integrate **Cloudinary** for product image uploads.
- Ensure **role-based access** so only admins can manage products.

---

### **Step 4: Payment Integration for Orders**

- Integrate **Stripe** for payment processing.
- Set up the **checkout process** (address input, order summary, payment).

---

### **Step 5: Customer Shopping Experience**

- Create a **homepage** with product listings, categories, and search functionality.
- Implement **product details pages** and allow adding items to the cart.
- Set up **shopping cart** and **wishlist** using React Context.
- Ensure a **responsive design** using Tailwind CSS.

---

### **Step 6: Order Management**

- Allow users to **track orders** and view order history.
- Admins can **manage order statuses** and track shipments.
- Implement **order status updates**
