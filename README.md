From command line

Docker

```
docker build -t intsys_healthcheck .
docker run -d --name intsys_healthcheck_1 intsys_healthcheck

```

## Set settingss
curl -v -H "Content-Type: application/json" -X POST https://fc.qa.u2035s.ru/healthcheck/settings/update -d '{"is_enabled":true}'
