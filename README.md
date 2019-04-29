From command line

Docker

```
docker build -t intsys_healthcheck .
docker run -d --name intsys_healthcheck_1 intsys_healthcheck

```

## Set settingss
curl -v -H "Content-Type: application/json" -X POST http://127.0.0.1:8009/healthcheck/set_settings -d '{"is_enabled":false}'