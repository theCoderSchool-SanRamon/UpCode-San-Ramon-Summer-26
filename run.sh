#!/bin/sh
.venv/bin/python3 src/backend/middleware.py &
pnpm run dev
