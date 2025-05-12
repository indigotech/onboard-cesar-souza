# Onboarding - Cesar Henrique

## Description

Initial project for learning and becoming familiar with tools and processes.

## **Environment and Tools**
### **Technologies Used:**
- **Python**: 3.11.6
- **FastAPI**: 0.115.12
- **Uvicorn**: 0.34.2
- **SQLAlchemy**: 2.0.40
- **PostgreSQL**: 17.4
- **Psycopg2-binary**: 2.9.10
- **Python-dotenv**: 1.1.0
### **Development Tools:**
- **Poetry**: Dependency management and packaging tool
- **Mypy**: 1.15.0
### **Docker**:
- **PostgreSQL** container for local development and testing environments.
## **Steps to Run and Debug**
### **1. Prerequisites**
Before running the project, ensure you have the following installed on your machine:
- **Docker**
- **Pyenv**
- **Python 3.11.6**
- **Poetry**
### **2. Clone the repository**
Clone the project to your local machine:
```bash
git clone https://github.com/indigotech/onboard-cesar-souza.git
cd onboard-cesar-souza
```
### **3. Setting up Environment Variables**
Create a `.env` file in the root of the project and add the following variables:
```bash
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_postgres_db_name
TEST_USER=your_test_user
TEST_PASSWORD=your_test_password
TEST_DB=your_test_db_name
DATABASE_URL=postgresql+asyncpg://user:password@localhost/db
```
### **4. Setting up PostgreSQL with Docker**
Run the following command to start the PostgreSQL container:
```bash
docker-compose up -d
```
This will spin up two PostgreSQL containers (localdb and testdb) on ports `5432` and `5433`, respectively.
### **5. Install dependencies**
Install the necessary dependencies using Poetry:
```bash
poetry install
```
### **6. Run the application**
To start the FastAPI application, use the command:
```bash
poetry run serve
```
This will start the server at `http://localhost:8000`.
