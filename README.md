# # SinMancha Running Club - Personal Trainer Platform

## 📋 Description

I built SinMancha to manage personal training businesses. The app helps trainers manage clients, memberships and events, and lets clients register and buy memberships. I developed this project (Ana Sousa) and it was inspired by my partner, Paul Ola.

**Project Theme:** "SinMancha" means "unspotted" or "without stains" in Spanish—symbolizing redemption and the power to transform your life, no matter where you've come from.

---

## ✨ Features

### Core Functionality
- **Multi-role system:** Trainer and client dashboards with distinct capabilities
- **Membership plans:** Flexible pricing and billing intervals per trainer
- **Event management:** Running clubs, classes, fitness challenges with capacity limits
- **Client registration:** Complete registration with profile creation
- **Payment processing:** Stripe integration for membership purchases
- **Exercise recommendations:** BMI-based exercise plans with personalized recommendations
- **Admin dashboard:** Comprehensive analytics and management interface

### Authentication & Security
- Django-allauth for secure authentication (supports email/username login)
- Django sites framework integration
- Environment-based secret key management
- CSRF protection, secure cookies, and clickjacking prevention

### UI/UX
- Responsive hero carousel with auto-rotation
- Mobile-friendly hamburger navigation
- Event cards with images and filtering
- Tiered membership plan cards
- Testimonials and community sections
- Modern CSS with flexbox and media queries

---

## 🖼 Wireframes & Screenshots

All images are stored in:

`static/img/screenshots/`

### Core Pages (UI Evidence)

- Homepage  
  ![Homepage](static/img/screenshots/homepage.png)

- Membership Plans  
  ![Membership Plans](static/img/screenshots/membership-plan.png)

- Membership (Unsubscribed)  
  ![Membership Unsubscribed](static/img/screenshots/membership-unsubscribed.png)

- Events Page  
  ![Events](static/img/screenshots/events.png)

- Client Dashboard  
  ![Client Dashboard](static/img/screenshots/client-dashboard.png)

- Exercise Plan  
  ![Exercise Plan](static/img/screenshots/exercise-plan.png)

- Payment Successful  
  ![Payment Successful](static/img/screenshots/payment-successful.png)

- Stripe Checkout  
  ![Stripe Checkout](static/img/screenshots/stripe-payment.png)

- Login Success  
  ![Login Success](static/img/screenshots/success-login.png)

### Validation & Performance Evidence

- W3C HTML Validator  
  ![W3C HTML Validator](static/img/screenshots/html-validator.png)

- W3C CSS Validator  
  ![W3C CSS Validator](static/img/screenshots/css-validator.png)

- Lighthouse Report  
  ![Lighthouse](static/img/screenshots/lighthouse.png)

### Wireframes
- Wireframe  
  ![Wireframe](static/img/screenshots/wireframe.png)

---

## 🌍 Live Deployment

The project is deployed using Heroku.

**Live URL:**  
https://sm5k-7156833a6677.herokuapp.com/

**Admin panel:**  
https://sm5k-7156833a6677.herokuapp.com/admin/

---

## 🧠 User Stories (Agile Planning)

### As a Trainer
- I want to create membership plans so I can offer structured pricing tiers.
- I want to host events so I can manage running clubs and classes.
- I want to view client registrations so I can monitor attendance.
- I want to see active memberships so I can track engagement.

### As a Client
- I want to register an account so I can access members-only features.
- I want to purchase a membership so I can join events.
- I want to join events so I can participate in training sessions.
- I want to generate a personalised exercise plan so I can improve safely.
- I want to view my dashboard so I can track my progress.

### As an Admin
- I want to manage users and roles to maintain system integrity.
- I want to monitor payments to verify transactions.
- I want to oversee memberships and events across the platform.

---

## 🗄 Database Design & ERD

The application uses a relational database structure built with Django ORM.

### Core Models
- `TrainerProfile` (One-to-One with User)
- `ClientProfile` (One-to-One with User)
- `MembershipPlan` (ForeignKey to TrainerProfile)
- `Membership` (ForeignKey to ClientProfile and MembershipPlan)
- `Event` (ForeignKey to TrainerProfile)
- `EventRegistration` (ForeignKey to Event and ClientProfile)
- `Payment` (linked to Membership and User)

### Key Relationships
- A `User` can have either a `TrainerProfile` or `ClientProfile`.
- A `Trainer` can create multiple `MembershipPlans`.
- A `Client` can purchase multiple `Memberships (only one active at a time)`.
- A `Trainer` can host multiple `Events`.
- Clients register for events via `EventRegistration`.
- Payments support membership activation and tracking.

Add your ERD image here once created:

![ERD](static/img/screenshots/erd.png)

---

## 🔄 CRUD Functionality Overview

### Trainers
- Create membership plans and events
- View client memberships and registrations
- Update event details and plans
- Delete events or deactivate plans

### Clients
- Register account and create profile
- Join and leave events
- View membership and exercise plan
- Update profile information

### Admin
- Full CRUD access through Django Admin dashboard

---

## 🧪 Testing Strategy

### Automated Testing
Tests were executed using:

`python manage.py test`

### Manual Testing
Manual testing included:
- Authentication (register/login/logout)
- Membership purchase via Stripe test mode
- Event joining/leaving and capacity rules
- Exercise plan generation across BMI ranges
- Role-based dashboard access
- Responsive display checks on mobile/tablet/desktop

### Validation Tools
- W3C HTML Validator
- W3C CSS Validator
- Lighthouse (Accessibility + Best Practices + Performance)

Screenshots for evidence are included above.

---

## 📈 Challenges & Problem Solving

During development I worked through:
- Fixing 500 errors caused by OneToOne relationship checks in templates
- Managing Stripe keys securely after GitHub push protection flagged exposed secrets
- Debugging differences between local development and Heroku deployment
- Resolving URL/view mismatches during refactoring
- Ensuring the UI changes correctly based on active membership status

These challenges strengthened my understanding of:
- Django permissions and role-based access
- Secure environment variable workflows
- Deployment debugging and logs
- Git version control and secret scanning

---

## 🔮 Future Improvements

If given more time, I would add:
- Membership cancellation and downgrade handling
- Payment history page for clients
- Trainer UI for editing events and plans (without admin)
- Automated email confirmations
- More analytics inside dashboards
- Additional Lighthouse optimisation and accessibility improvements
- Docker container support for easier deployment

---

## 🪞 Reflection

This project helped me build confidence in designing, building, testing, and deploying a full-stack Django app.

The hardest part was integrating Stripe payments securely while also ensuring the deployed version worked exactly the same as local development. Debugging production issues forced me to learn how to read logs properly, trace template errors, and manage environment variables correctly.

Overall, SinMancha demonstrates my ability to:
- Design a relational database structure
- Build a multi-role secure Django system
- Integrate payments
- Create responsive UI
- Deploy and document a complete project

---

## 🛠 Tech Stack

- **Backend:** Django 6.0.1, Python 3.14+
- **Database:** SQLite (development) / PostgreSQL (production recommended)
- **Authentication:** django-allauth 0.50.0
- **Payments:** Stripe API (test mode)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Image Processing:** Pillow
- **Environment Config:** python-dotenv


## 🚀 Local Development Setup

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd sinmancha
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with:
```env
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Stripe Test Keys (from https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_SECRET_HERE  # Optional for webhook testing

# Database (optional, defaults to SQLite)
# DATABASE_URL=postgresql://user:password@localhost:5432/sinmancha
```

### 3. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Create Initial Data (Optional)

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from club.models import TrainerProfile, MembershipPlan
from django.utils import timezone

   # Create a trainer (example account)
   user = User.objects.create_user(username='anasousa', password='secure123', email='ana@example.com')
   trainer = TrainerProfile.objects.create(
      user=user,
      display_name='Ana Sousa',
      bio='Certified personal trainer and running coach.'
   )

# Create a membership plan
plan = MembershipPlan.objects.create(
    name='Starter',
    description='Perfect for beginners',
    price=29.99,
    billing_interval='month',
    trainer=trainer,
    is_active=True
)

### 4.a Adding events (quick)

You can add events either manually in the Django shell or using the provided scripts.

Option A — Django shell (quick, manual):

```python
from django.contrib.auth.models import User
from club.models import TrainerProfile, Event
from django.utils import timezone
import datetime

# ensure trainer exists
trainer = TrainerProfile.objects.first()

Event.objects.create(
   title='Morning Fitness Class',
   trainer=trainer,
   date=timezone.now().date() + datetime.timedelta(days=1),
   start_time=timezone.now().time(),
   capacity=20,
   event_type='class',
   description='Sample class',
)
```

Option B — Use helper script (recommended for multiple events):

Run the script that creates sample events and assigns future dates:

```bash
heroku run python scripts/fix_events_dates.py -a <your-heroku-app>   # on Heroku
python scripts/fix_events_dates.py                                   # locally (after venv & env)
```

After adding events, visit `/events/` to confirm they are visible (events must have `date >= today` and `is_cancelled=False`).

```

### 5. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

**Default Admin URL:** http://127.0.0.1:8000/admin/

## 💳 Stripe Configuration

### Test Mode Setup
1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Switch to **Test Mode** (toggle in top-right)
3. Navigate to **Developers** → **API Keys**
4. Copy `Secret Key` and `Publishable Key` into `.env`

### Test Cards
- **Success:** `4242 4242 4242 4242`
- **Declined:** `4000 0000 0000 0002`
- **Requires Auth:** `4000 0025 0000 3155`
- Any future expiry date and any 3-digit CVC



## 🗄 Database Configuration

### Development (SQLite)
Default; no configuration needed. Database file: `db.sqlite3`

### Production (PostgreSQL)

#### Option 1: Using DATABASE_URL (Recommended for Heroku)
```env
DATABASE_URL=postgresql://username:password@localhost:5432/sinmancha
```

#### Option 2: Individual Environment Variables
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=sinmancha
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

Then in `settings.py`, uncomment the PostgreSQL config.

### Create PostgreSQL Database

```bash
# On macOS/Linux
createdb sinmancha
createuser sinmancha_user -P  # Set password when prompted

# On Windows (in psql)
CREATE DATABASE sinmancha;
CREATE USER sinmancha_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE sinmancha TO sinmancha_user;
```

### Run Migrations

```bash
python manage.py migrate
```

## 📁 Project Structure

```
sinmancha/
├── club/                    # Main app: trainers, clients, events
│   ├── models.py            # TrainerProfile, ClientProfile, Event, Membership
│   ├── views.py             # Views for home, events, memberships, dashboards
│   ├── urls.py              # URL routing
│   └── exercise_recommendations.py  # BMI-based exercise plans
├── payments/                # Stripe payment handling
│   ├── models.py            # Payment, Invoice records
│   ├── views.py             # Checkout, success, webhook handlers
│   └── urls.py              # Payment URLs
├── sinmancha/               # Project config
│   ├── settings.py          # Django settings, env var loading
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI application
├── templates/               # HTML templates
│   ├── base.html            # Base layout (nav, footer)
│   ├── home.html            # Home page with carousel and testimonials
│   ├── events.html          # Events listing and filtering
│   ├── membership_plans.html # Membership tier cards
│   └── payments/            # Payment templates (success, cancel)
├── static/                  # Static assets
│   ├── css/style.css        # Global styles
│   └── img/                 # Images (hero, testimonials, events)
├── .env.example             # Template for environment variables
├── requirements.txt         # Python dependencies
└── manage.py                # Django management script
```

## 👤 User Roles

### Trainers
- Create and manage membership plans
- Host events (running clubs, classes, challenges)
- View client progress and memberships
- Trainer dashboard: analytics, client list, event schedule

### Clients
- Register and create profiles
- Purchase memberships
- View and join events
- Track personal records and exercise plans
- Client dashboard: active membership, upcoming events, exercise recommendations

### Admin
- Manage users and roles
- Monitor all memberships and payments
- View event registrations and capacity
- System-wide analytics

## 🔐 Security Best Practices

### Development
- Keep `.env` and `.env.local` in `.gitignore` (already configured)
- Use Stripe **test keys** only
- `DEBUG = True` is acceptable for development

### Production

**Before deploying:**

1. **Generate a new SECRET_KEY:**
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```
   Add to production `.env`

2. **Set environment variables:**
   ```env
   SECRET_KEY=<generated-key>
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   STRIPE_SECRET_KEY=sk_live_YOUR_LIVE_KEY
   STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_LIVE_KEY
   DATABASE_URL=postgresql://...
   ```

3. **Enable security middleware:**
   - `SECURE_SSL_REDIRECT = True`
   - `SESSION_COOKIE_SECURE = True`
   - `CSRF_COOKIE_SECURE = True`
   - `SECURE_HSTS_SECONDS = 31536000`

4. **Never commit secrets** to version control

## 🚢 Deployment — simple steps I use

I keep deployment simple so anyone can follow it. Below are two easy options: Heroku (fast) and AWS Elastic Beanstalk (a managed AWS option). I write these steps as if I'm doing them myself.

### Option 1 — Heroku (quick, recommended for demos)

Prereqs: Heroku account and Heroku CLI installed.

1) Login and create the app

```bash
heroku login
heroku create my-sinmancha-app
```

2) Set config (secrets) — change values to yours:

```bash
heroku config:set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=my-sinmancha-app.herokuapp.com
heroku config:set STRIPE_SECRET_KEY=sk_test_...
heroku config:set STRIPE_PUBLISHABLE_KEY=pk_test_...
```

3) Add Postgres (optional for production-like DB):

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

4) Prepare and push

```bash
pip freeze > requirements.txt
echo "web: gunicorn sinmancha.wsgi --log-file -" > Procfile
git add requirements.txt Procfile
git commit -m "Prepare for Heroku"
git push heroku main
```

5) Run migrations and collect static

```bash
heroku run python manage.py migrate
heroku run python manage.py collectstatic --noinput
heroku run python manage.py createsuperuser
```

6) Hook Stripe (in Stripe dashboard add webhook to `https://my-sinmancha-app.herokuapp.com/payments/webhook/` and then run `heroku config:set STRIPE_WEBHOOK_SECRET=whsec_...`)

That's it — I open the app with `heroku open`.

### Option 2 — AWS (use Elastic Beanstalk for an easier AWS experience)

Elastic Beanstalk manages servers for you so you don't deal with low-level details.

1) Install EB CLI and log in

```bash
pip install awsebcli --upgrade
eb init -p python-3.10 my-sinmancha-app --region eu-west-1
```

2) Create an environment and deploy

```bash
eb create my-sinmancha-env
eb deploy
```

3) Set environment variables (secrets)

```bash
eb setenv SECRET_KEY=... DEBUG=False ALLOWED_HOSTS=your-domain.com STRIPE_SECRET_KEY=... STRIPE_PUBLISHABLE_KEY=...
```

4) (Optional) Add an RDS database from the Elastic Beanstalk console or connect an existing RDS instance and set `DATABASE_URL` in `eb setenv`.

5) Configure static/media with S3 if you want persistent uploads. Install `django-storages[boto3]` and set AWS keys as environment variables.

Why I like Elastic Beanstalk: it gives me a managed server and is simpler than configuring EC2/Nginx/Gunicorn manually.

### Quick pre-deploy checklist (what I always do)

- Generate a new `SECRET_KEY` and set it in the production env
- Set `DEBUG=False` and `ALLOWED_HOSTS` correctly
- Use a Postgres DB for production (Heroku Postgres or RDS)
- Set Stripe keys and webhook secret as environment variables
- Use S3 + `django-storages` for user uploads (optional but recommended)
- Collect static files and verify they serve correctly
- Make sure HTTPS is enabled for your domain

---


#### Run specific app tests
```bash
python manage.py test club          # Test club app
python manage.py test payments      # Test payments app
```

#### Run specific test class
```bash
python manage.py test club.tests.MembershipTestCase
```

#### Run with verbose output
```bash
python manage.py test --verbosity=2
```

#### Run with coverage report (if coverage installed)
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Coverage

The test suite includes:

#### Club App Tests (`club/tests.py`)
- **TrainerProfileTestCase**: Trainer profile creation and string representation
- **ClientProfileTestCase**: Auto-creation of client profiles, active membership detection
- **MembershipPlanTestCase**: Membership plan creation and billing intervals
- **MembershipTestCase**: Auto-calculation of membership end dates, active status properties
- **EventTestCase**: Event creation, past event detection, capacity and registration tracking
- **EventRegistrationTestCase**: Registration creation, unique constraint validation
- **AuthenticationViewsTestCase**: Login requirements, permission-based access control
- **FormValidationTestCase**: Membership activation validation, error handling

#### Payments App Tests (`payments/tests.py`)
- **PaymentModelTestCase**: Payment creation, status transitions, unique constraint validation
- **PaymentViewsTestCase**: Checkout session creation, authentication requirements
- **PaymentSecurityTestCase**: Payment ownership validation, user isolation

### Manual Testing Checklist

#### User Registration & Authentication
- [ ] Register new account successfully
- [ ] Login with credentials
- [ ] Logout clears session
- [ ] Protected pages redirect to login
- [ ] Registered users redirected away from login page

#### Memberships
- [ ] View membership plans without login
- [ ] Cannot activate membership without client profile
- [ ] Cannot have two active memberships
- [ ] Membership end date calculated correctly (30 days for monthly, 365 for yearly)
- [ ] Active membership property reflects true status

#### Events
- [ ] View all upcoming events
- [ ] Filter events by type (running club, class, challenge)
- [ ] Filter events by distance
- [ ] Cannot join full event
- [ ] Can join and leave events
- [ ] Past events marked as cancelled
- [ ] Event capacity cannot be exceeded

#### Payments (Stripe Test Mode)
- [ ] Checkout page loads with Stripe form
- [ ] Test card (4242 4242 4242 4242) processes successfully
- [ ] Declined card (4000 0000 0000 0002) shows error
- [ ] Success page displays after payment
- [ ] Payment record created in database
- [ ] Membership activated after successful payment
- [ ] Cancel page displays if payment cancelled

#### Exercise Plans
- [ ] Form loads when logged in
- [ ] BMI calculated correctly from weight/height
- [ ] Exercise plan generated for all BMI categories
- [ ] Plan changes based on selected goal
- [ ] API endpoint requires authentication

#### Responsive Design
- [ ] Mobile hamburger menu toggles
- [ ] Menu closes when link is clicked
- [ ] All pages readable on mobile (375px width)
- [ ] All pages readable on tablet (768px width)
- [ ] All pages readable on desktop (1024px+ width)
- [ ] Images scale appropriately
- [ ] Navigation is accessible on all sizes

#### Browser Compatibility
- [ ] Chrome/Chromium (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Known Issues

None currently identified. All core functionality has been tested and works as expected.

### Debugging Tips

#### View logs while running
```bash
python manage.py runserver --verbosity=2
```

#### Test database queries
```bash
python manage.py shell
>>> from club.models import Event
>>> Event.objects.all().query  # See SQL query
```

#### Clear database and start fresh
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## 📊 Project Requirements Compliance

This project satisfies the following requirements:

- ✅ **Full-stack Django application** with multiple apps (club, payments)
- ✅ **Relational database** with custom models (TrainerProfile, ClientProfile, Event, Membership, Payment, Invoice)
- ✅ **E-commerce integration** (Stripe checkout, payments, webhooks)
- ✅ **Forms with validation** (membership signup, event registration, exercise plans)
- ✅ **JavaScript** (carousel auto-rotation, hamburger menu, form interactions)
- ✅ **Responsive design** (mobile-friendly, media queries, flexbox)
- ✅ **Authentication & authorization** (django-allauth, role-based dashboards)
- ✅ **Admin interface** (Django admin for model management)
- ✅ **Documentation** (README, setup guides, deployment instructions)
- ✅ **Version control** (GitHub repository)
- ✅ **Security** (env vars for secrets, CSRF, clickjacking protection, secure headers)

## 🤝 Contributing

To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a Pull Request

## 📝 License

This project is part of a course assignment. All rights reserved.

## 👏 Acknowledgments

- Inspired by the work and needs of Paul Ola (my partner)
- Django documentation and best practices
- Stripe API documentation
- Bootstrap and modern web design principles

**Last Updated:** February 2026
**Version:** 1.0.0
**Django Version:** 6.0.1

## Author

Ana Sousa

