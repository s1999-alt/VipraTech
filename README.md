# VipraTech Django Assignment

A simple Django + Stripe application for purchasing fixed products and viewing paid orders.

---

### Tech Stack
- Python 3.x
- Django 5.x
- Postgresql
- Stripe Checkout API
- Bootstrap 5

## Features
- 3 fixed products shown on the homepage.
- Stripe Checkout integration (Test Mode).
- Prevents double submissions using Stripe session IDs.
- Authenticated users can purchase and view their own orders.
- Bootstrap UI.
- Dockerized backend and database for easy deployment.

---

## Assumptions
- Single-page flow for simplicity (all products and orders visible on one page).
- Using **Stripe Checkout** instead of Payment Intents for simplicity and reliability.
- Users must be logged in to buy products.

---

## Flow Chosen
**Stripe Checkout** was chosen because it:
- Handles payment UI, success/cancel redirects automatically.
- Reduces chances of duplicate charges.
- Simpler to integrate.

---

## Avoiding Double Charge / Inconsistent State
- No order is created before payment. Only a Stripe Checkout Session is generated.
- After successful payment, Stripe redirects back with a `session_id` which is then verified using the Stripe API.
- The order is created **only if**:
  - the session is valid,
  - the payment status is `"paid"`,
  - the session has not been used before (idempotent creation).
- This prevents:
  - ghost/unpaid orders,
  - duplicate orders from refresh,
  - inconsistent payment states.

---

## ⚙️ Docker Setup & Run Steps

1. **Clone the repo**
   ```bash
   git clone https://github.com/s1999-alt/VipraTech.git
   cd Vipratech


2. **Create .env file**
  - Use .env.example as a template.
  - Add your Stripe keys and database configuration.

3. **Build and run containers**   
```bash
docker-compose up --build
``` 

4. **Create superuser (inside container)**
```bash
docker-compose exec vipratech_backend python manage.py createsuperuser
``` 
- Follow prompts to set username, email, and password.

5. **Access the application**
- Django backend: http://localhost:8000

- Admin panel: http://localhost:8000/admin


### Notes on Code Quality

- Used clear separation of concerns (models, views, templates).

- Environment variables handled using python-os.getenv().

- Used Django authentication for secure access to “My Orders”.

- Applied Bootstrap for responsive UI.

- Dockerized for consistent environment setup.


### AI Tool Used: ChatGPT (OpenAI GPT-5)

**Assisted in:**
- Structuring Django + Stripe checkout flow.
- Designing the index.html and base.html layout.
- Creating README.md structure.

- All code was reviewed, tested, and understood manually before submission.


### Time Spent

**⏱ Total Time Spent:** ~12 hours


### Improvements

The current flow creates an order **only after** Stripe confirms that the payment was successful.  
This eliminates ghost orders and keeps the system consistent for synchronous payments (most card transactions).

However, some payment methods—like UPI, netbanking, or delayed confirmation methods—may not redirect the user back immediately.  
If the user closes the browser or loses connection, the backend will never receive the `success` request.

### Proposed Improvement — Use Stripe Webhooks

Using Stripe Webhooks would make the system fully reliable because:

- Stripe sends an event (e.g., `checkout.session.completed`) to the backend even if the user never returns to the website.
- Orders can be created or updated automatically upon receiving this event.
- Prevents missing orders or incorrect statuses for delayed-payment methods.
- Makes the system production-ready and more resilient.

With webhooks:
1. Checkout session is created.  
2. User pays on Stripe.  
3. Stripe triggers the webhook.  
4. Backend verifies payment and creates the order (idempotently).  
5. Redirect flow becomes optional.

This upgrade ensures 100% accuracy for all payment scenarios.

