# A Python web project with unittest

The project is a Open Taobao Platform web app with only one api to oauth and get the logined user's shop info.

## install

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## test

```bash
pytest
```

## run

```bash
# set needed environment variables:APP_KEY, APP_SECRET, APP_DOMAIN, REDIRECT
uvicorn app.main:app
```

## Author

Du Yixian
