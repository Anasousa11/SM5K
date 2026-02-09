# Security & Development Setup Guide

## Environment Variables Configuration

### Development Environment Setup

1. **Create `.env` file in project root:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your local values:**
   ```env
   # Django
   SECRET_KEY=django-insecure-dev-key-only-use-in-development
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Stripe Test Mode
   STRIPE_SECRET_KEY=sk_test_51234567890ABCDEFGHIJKLMNOP
   STRIPE_PUBLISHABLE_KEY=pk_test_51234567890ABCDEFGHIJKLMNOP
   STRIPE_WEBHOOK_SECRET=whsec_test_1234567890

   # Database (optional - uncomment for PostgreSQL local)
   # DATABASE_URL=postgresql://postgres:password@localhost:5432/sinmancha
   ```

3. **Verify `.env` is in `.gitignore`:**
   ```bash
   cat .gitignore | grep ".env"
   # Should output: .env
   ```

### Production Environment Setup

**Never commit `.env` to Git!** Use your deployment platform's secret management:

#### For Heroku:
```bash
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set STRIPE_SECRET_KEY="sk_live_..."
heroku config:set STRIPE_WEBHOOK_SECRET="whsec_live_..."
```

#### For AWS / Self-Hosted:
Use environment variable files, system environment, or secret managers:
- AWS Secrets Manager
- HashiCorp Vault
- System environment variables
- `.env.production` (not in Git!)

## Running the Development Server

### 1. Activate Virtual Environment
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Apply Migrations
```bash
python manage.py migrate
```

### 4. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (create secure password)
```

### 5. Run Development Server
```bash
python manage.py runserver
```

Server runs at: **http://127.0.0.1:8000/**
Admin panel: **http://127.0.0.1:8000/admin/**

## Testing Stripe Integration

### Stripe Test Mode Cards

Use these test cards in the checkout form (expiry and CVC can be any future date and 3 digits):

| Card Number | Result | Use Case |
|---|---|---|
| `4242 4242 4242 4242` | ✅ Success | Test successful payment |
| `4000 0000 0000 0002` | ❌ Declined | Test payment failure |
| `4000 0025 0000 3155` | 🔐 3D Secure | Test authentication flow |
| `5555 5555 5555 4444` | ✅ Mastercard | Test different card type |

### Test a Membership Purchase

1. Navigate to **Memberships** page
2. Click **Buy Now** on any plan
3. You'll be redirected to Stripe test checkout
4. Enter test card: `4242 4242 4242 4242`
5. Any future expiry date (e.g., `12/25`)
6. Any 3-digit CVC (e.g., `123`)
7. Click **Pay**
8. Confirm payment on success page
9. Check admin to verify `Payment` record created

### Test Webhook (Local Development)

To test webhooks locally without deploying:

1. **Install Stripe CLI:**
   - Download from https://stripe.com/docs/stripe-cli
   - Or: `brew install stripe/stripe-cli/stripe` (macOS)

2. **Login to Stripe CLI:**
   ```bash
   stripe login
   # Paste your restricted API key when prompted
   ```

3. **Forward events to local server:**
   ```bash
   stripe listen --forward-to localhost:8000/payments/webhook/
   ```

4. **Copy the webhook signing secret** shown in terminal

5. **Add to `.env`:**
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_test_your_secret_from_cli
   ```

6. **Trigger test events:**
   ```bash
   stripe trigger payment_intent.succeeded
   stripe trigger charge.refunded
   ```

## Project Requirements Verification

This project fulfills all course requirements:

### ✅ Full-Stack Django Application
- Django 6.0.1 with 2 apps (club, payments)
- Multiple URL patterns and views
- Custom context processors

### ✅ Relational Database & Models
- TrainerProfile (OneToOne with User)
- ClientProfile (OneToOne with User, FK to TrainerProfile)
- MembershipPlan (FK to TrainerProfile)
- Membership (FK to User & MembershipPlan)
- Event (FK to TrainerProfile, EventType choices)
- EventRegistration (FK to User & Event, unique_together)
- Payment (FK to User & MembershipPlan)
- Invoice (FK to User & Payment)

### ✅ E-Commerce Integration
- Stripe checkout.Session for payments
- webhook endpoint for asynchronous events
- Payment model tracking transactions
- Membership activation on successful payment

### ✅ Forms with Validation
- Django-allauth registration form (validated)
- Event registration form (capacity limits)
- Exercise recommendation form (numeric validation)
- Admin forms for model creation

### ✅ JavaScript Functionality
- Carousel auto-rotation (6-second interval)
- Carousel indicator clicks
- Hamburger menu toggle (mobile nav)
- Exercise plan form submission (AJAX-ready)
- Payment form interactions (Stripe.js compatible)

### ✅ Responsive Design
- Mobile-first CSS approach
- Media queries (600px, 900px breakpoints)
- Hamburger navigation for mobile
- Flexbox layouts
- Touch-friendly buttons and spacing

### ✅ Authentication & Authorization
- Django-allauth for signup/login/logout
- Role-based views (client_dashboard, trainer_dashboard, admin_dashboard)
- @login_required decorators
- @user_passes_test decorators
- Profile existence checks

### ✅ Admin Interface
- Django admin for all models
- Custom admin actions
- Filter and search capabilities
- Bulk operations

### ✅ Security
- Environment variables for secrets
- CSRF protection enabled
- XFrame protection (clickjacking)
- Secure password validators
- SQL injection prevention (ORM)
- ALLOWED_HOSTS configuration
- No hardcoded secrets in codebase

### ✅ Documentation
- Comprehensive README.md
- DEPLOYMENT.md with 4 deployment options
- .env.example with all variables
- Code comments in views and models
- Setup instructions for local development

### ✅ Version Control
- Git repository with .gitignore
- Meaningful commit history (to be added)
- README with attribution

## Next Steps

1. **Activate Virtual Environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Create `.env` File:**
   ```bash
   cp .env.example .env
   # Edit with your Stripe test keys
   ```

3. **Run Development Server:**
   ```bash
   python manage.py runserver
   ```

4. **Test Application:**
   - Visit http://127.0.0.1:8000
   - Create account via Sign Up
   - Purchase membership with test card
   - Check admin panel for records

5. **Deploy When Ready:**
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for platform-specific instructions
   - Generate production SECRET_KEY
   - Configure production environment variables
   - Switch to PostgreSQL for production

## Common Commands

```bash
# Virtual Environment
source venv/bin/activate          # Activate (macOS/Linux)
venv\Scripts\activate             # Activate (Windows)
deactivate                        # Deactivate

# Django Management
python manage.py runserver        # Start dev server
python manage.py makemigrations   # Create migration files
python manage.py migrate          # Apply migrations
python manage.py shell            # Django shell
python manage.py createsuperuser  # Create admin user
python manage.py collectstatic    # Collect static files

# Database
python manage.py dbshell         # Database shell
python manage.py dumpdata > backup.json  # Backup database
python manage.py loaddata backup.json    # Restore database

# Testing
python manage.py test            # Run tests
python manage.py test club       # Test specific app

# Dependencies
pip install -r requirements.txt  # Install all
pip freeze > requirements.txt    # Update requirements
pip install package_name         # Install new package
```

---

**Last Updated:** February 2026
**Version:** 1.0.0
**Django Version:** 6.0.1
**Python Version:** 3.10+
