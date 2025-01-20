# University Course Scheduling Project

This project is a **Constraint Satisfaction Problem (CSP)** implementation for scheduling university courses. It provides a robust backend API for managing schedules efficiently and integrates with a custom frontend available at [uni-schedule repository](https://github.com/devalimotahari/uni-schedule). This system aims to automate and optimize the scheduling process, making it easier to manage professors, timeslots, and course allocations.

---

## Running the Project Without Docker

### 1. Install the Environment
```bash
python -m venv env

source env/bin/activate

pip install -r requirements.txt
```

### 2. Run the Application
```bash
uvicorn app.main:app --reload
# or
python -m uvicorn app.main:app --reload
```

---

## Running the Project Using Docker

### 1. Build and Start the Containers
```bash
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml up
```

### 2. Port Configuration
The default port is `8000`. To use a different port, you can export a custom `APP_PORT` value before running the containers:
```bash
export APP_PORT=8001
```

---

## Features
- **Custom Frontend:** Integrated frontend available in a separate repository.
- **API-First Design:** Provides a flexible API for integration with other systems.
- **Optimized Scheduling:** Handles complex constraints for university scheduling.

---

## Technologies Used
- **FastAPI:** Framework for building the API.
- **Google OR-Tools:** Primary CSP solver.
- **SQLAlchemy and SQLModel:** Database interaction and ORM.
- **Pydantic:** Data validation and parsing.
- **JWT Auth:** Secure authentication mechanism.

---

## TODOs
- [ ] Add logging for better debugging and monitoring.
- [ ] Add comments to the codebase, especially for classes and complex logic.
- [ ] Parse multi-range professor timeslots into a single range if they are connected.

---

Feel free to contribute to the project or report issues to help us improve the scheduling system!

