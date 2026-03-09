# laos-events

Laos in Bloom — March & April 2026 events website. Static site listing festivals, markets, and cultural events in Laos.

## Live

https://laos-events.shellnode.lol

## Stack

- Static HTML/CSS/JS (vanilla, no frameworks)
- nginx:alpine container
- Ghost VPS / Docker
- SSL via SWAG + Cloudflare DNS

## Run Locally

    docker build -t laos-events-app .
    docker run -p 8080:80 laos-events-app

## Deploy

    docker context use ghost
    docker compose up -d --build

## Data Sources

- Images: icrawler (Bing/Baidu)
- Event data: manually curated
