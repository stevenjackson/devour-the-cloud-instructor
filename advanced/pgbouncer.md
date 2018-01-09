

CHANGE 

```python
DATABASES = {
    'default': dj_database_url.config(
        default='postgres://saleor:saleor@127.0.0.1:5432/saleor',
        conn_max_age=600)}
```

TO (just changing connection string port number from **5432** to **6432**)

```python
DATABASES = {
    'default': dj_database_url.config(
        default='postgres://saleor:saleor@127.0.0.1:6432/saleor',
        conn_max_age=600)}
```
