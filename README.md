# FitBuddy — AI Fitness Plan Generator using Gemini Models

FitBuddy is an AI-powered fitness planning web application that generates a personalized 7-day workout plan and a practical nutrition and recovery suggestion based on user input.

## Features

* AI-generated 7-day workout plans
* Personalized plans based on age, weight, goal, and preferred intensity
* AI-generated nutrition and recovery guidance
* Feedback-based workout plan updates
* SQLite database integration
* FastAPI backend
* Server-rendered HTML interface using Jinja2
* Structured AI responses using Pydantic schemas
* Environment-based API key configuration
* Safety-focused AI instructions

## How It Works

1. The user enters their basic information and fitness preferences.
2. FitBuddy sends the information to the Gemini API.
3. Gemini generates a structured 7-day workout plan.
4. A separate AI request generates a nutrition and recovery suggestion.
5. The generated plan is displayed on the results page.
6. User feedback can be used to update the workout plan.

## Tech Stack

| Technology | Purpose                                     |
| ---------- | ------------------------------------------- |
| Python     | Application development                     |
| FastAPI    | Web framework and API routes                |
| Gemini API | AI-generated fitness and nutrition content  |
| Pydantic   | Data validation and structured AI responses |
| SQLAlchemy | Database interaction                        |
| SQLite     | Local database                              |
| Jinja2     | HTML templating                             |
| HTML/CSS   | User interface                              |

## Project Structure

```text
FitBuddy/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── schemas.py
│   ├── services/
│   │   ├── gemini.py
│   │   └── formatting.py
│   ├── static/
│   │   └── style.css
│   └── templates/
│       ├── index.html
│       ├── result.html
│       ├── error.html
│       └── all_users.html
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── run_windows.bat
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/rankawatdurga296-art/FitBuddy.git
cd FitBuddy
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API

Create a `.env` file in the project root based on `.env.example`.

Add your API key:

```text
GEMINI_API_KEY=your_api_key_here
```

Do not commit the `.env` file or expose your API key publicly.

### 5. Run the application

```bash
uvicorn app.main:app --reload
```

Open the application at:

```text
http://127.0.0.1:8000
```

## AI Safety

FitBuddy includes safety instructions in its AI layer to discourage dangerous, extreme, or medically prescriptive fitness recommendations.

The application is intended as a general wellness planning tool and is not a replacement for qualified medical or fitness professionals.

## Demo

Screenshots and a demonstration video can be added here.

## Future Improvements

* User authentication
* Fitness progress tracking
* Exercise illustrations
* More workout customization
* Dashboard and analytics
* Cloud deployment
* Expanded test coverage

## Project

**FitBuddy — AI Fitness Plan Generator**

Built using Python, FastAPI, Gemini API, SQLAlchemy, SQLite, Pydantic, Jinja2, HTML, and CSS.
