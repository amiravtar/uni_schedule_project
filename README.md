# Not using docker
## Install the env
```bash
python -m venv env

source env/bin/activate

pip install -r requirements.txt
```

## run
```bsah
uvicorn app.main:app --reload
# or
python -m uvicorn app.main:app --reload
```

# Use docker

```bash
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml up
```

defualt port is 8000
you can change it via:
export APP_PORT=8001