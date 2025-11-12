#!/bin/bash
rm -rf chat_logs/*
uvicorn backend.main:app --port 9000