# AI Recruitment Platform

A modern recruitment platform leveraging AI to connect candidates and employers efficiently.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [AI Features](#ai-features)
- [Authentication Flow](#authentication-flow)
- [Storage](#storage)
- [Contributing](#contributing)

## Features

### For Candidates

- Create and manage professional profiles
- Upload and manage multiple resumes
- AI-generated professional bio based on skills and resume
- Apply to job postings with a single click
- Track application status across different jobs

### For Employers

- Create company profiles
- Post and manage job listings with AI-powered job description generation
- Browse candidate applications
- Get AI-powered candidate recommendations for specific roles
- Publish blog posts with AI-generated content

### Platform Features

- JWT-based authentication with secure HTTP-only cookies
- Email verification via OTP
- Password reset functionality
- Account deactivation/reactivation
- Role-based access control
- Cloud-based file storage

## Technology Stack

- **Backend**: Django 5.1.5, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **AI Integration**: OpenAI API
- **Storage**: Cloudinary (images), Backblaze B2 (resumes/documents)
- **Text Processing**: NLTK (Natural Language Toolkit)
- **Email**: Mailgun (configurable)

## Project Structure

```
Backend/
├── ai/                  # AI-related functionality
├── applications/        # Job applications
├── blogs/               # Blog post functionality
├── core/                # Project settings and core functionality
├── emails/              # Email templates and functionality
├── jobs/                # Job listings
├── users/               # User management
│   ├── views/           # User-related views split by role
│   ├── models.py        # User models
│   └── serializers.py   # User serializers
├── .env                 # Environment variables (not in repo)
├── manage.py            # Django management script
└── requirements.txt     # Project dependencies
```

## Installation and Setup

1. Clone the repository:

```bash
git clone [repository-url]
cd AI-Recruitment/Backend
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables (see [Environment Variables](#environment-variables) section).

5. Run migrations:

```bash
python manage.py migrate
```

6. Start the development server:

```bash
python manage.py runserver
```

## Environment Variables

Create a `.env` file in the Backend directory with the following variables:

```
# Django Settings
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# API Keys
OPENAI_TOKEN=your_openai_api_key
GITHUB_TOKEN=your_github_token
CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# Backblaze B2
B2_KEY_ID=your_b2_key_id
B2_APP_KEY=your_b2_app_key
B2_BUCKET_NAME=your_b2_bucket_name

# Email
MAILGUN_API_KEY=your_mailgun_api_key
SENDER_DOMAIN=your_sender_domain
DEFAULT_EMAIL=no-reply@yourdomain.com

# Frontend
FRONT_END_URL=localhost:3000
BASE_URL=http://localhost:8000
```

## API Documentation

### Authentication Endpoints

- `POST /api/users/signup/`: Register a new user
- `POST /api/users/login/`: Authenticate a user
- `POST /api/users/logout/`: Log out a user
- `POST /api/users/verify-email/`: Verify email with OTP
- `POST /api/users/resend-otp-email/`: Resend verification OTP
- `POST /api/users/token/refresh/`: Refresh JWT token

### User Management Endpoints

- `GET /api/users/me/`: Get current user profile
- `PUT/PATCH /api/users/update-me/`: Update current user profile
- `DELETE /api/users/delete-me/`: Delete current user account
- `POST /api/users/change-password/`: Change password
- `POST /api/users/change-username/`: Change username
- `POST /api/users/forget-password/`: Request password reset
- `POST /api/users/resetpassword/<token>`: Reset password with token

### Job Endpoints

- `GET /api/jobs/`: List all job postings
- `GET /api/jobs/<id>`: Get a specific job posting
- `POST /api/jobs/publish-job-post/`: Create a new job posting
- `GET /api/jobs/my-job-listings/`: List employer's job postings
- `GET/PUT/DELETE /api/jobs/my-job-listing/<id>`: Manage specific job posting

### Application Endpoints

- `POST /api/applications/apply/`: Apply for a job
- `GET /api/applications/job/<job_id>`: List applications for a job
- `PATCH /api/applications/job/<job_id>/update-status/`: Update application status

### Blog Endpoints

- `GET /api/blogs/`: List all published blogs
- `GET /api/blogs/latest/`: Get latest blogs
- `GET /api/blogs/<slug>`: Get specific blog post
- `POST /api/blogs/publish/`: Create a new blog post

### AI Endpoints

- `POST /api/ai/generate-job-post/`: Generate a job posting
- `POST /api/ai/generate-candidate-bio/`: Generate a candidate bio
- `POST /api/ai/generate-blog-post/`: Generate a blog post
- `POST /api/ai/recommend-candidate/`: Get candidate recommendations for a job

## AI Features

### Job Listing Generation

AI-powered job description generation based on minimal input like job title, company, and a brief description.

### Candidate Bio Generation

Automatically generates professional candidate bios from resumes and profile information.

### Blog Post Generation

Creates SEO-optimized blog posts on recruitment topics with customizable length and keywords.

### Candidate Recommendation

Analyzes candidate resumes against job descriptions to rank and recommend the best candidates.

### Content Filtering

Ensures all user-generated content meets professional standards by filtering inappropriate content.

## Authentication Flow

1. **Registration**: User signs up with name, email, password, and role
2. **Email Verification**: OTP is sent to the user's email for verification
3. **Login**: User logs in with email and password, receives JWT tokens via HTTP-only cookies
4. **Session Management**: Access token (15 min) and refresh token (7 days) handle authentication
5. **Token Refresh**: Automatic token refresh as needed

## Storage

- **Images**: User photos, employer logos, and blog thumbnails stored in Cloudinary
- **Documents**: Resumes stored in Backblaze B2 Storage
- **Database**: User data, job listings, and applications stored in PostgreSQL

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
