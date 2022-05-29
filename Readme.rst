shopauthdemo
************

Requirements
============

- At least python3.7+
- Shopify public or custom app created in dev dashboard.
- Ngrok started at port 5000.
- Ngrok urls placed into app settings.
- App set to embedded in app settings.

Setup `.env` with correct settings
==================================

`cp -n .env.example .env`

`nano -w .env`

Create virtual environment
==========================

`python -m venv ve`

Install packages
================

`ve/bin/pip install -e "."`


Start up server
===============

`ve/bin/gunicorn --bind 'localhost:5000' --reload 'shopauthdemo:main()'`

Open install link found in dev dashboard for given test shop
============================================================

Use your browser and find link.
