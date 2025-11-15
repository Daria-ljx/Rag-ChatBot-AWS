#!/bin/bash

echo "🧹 Cleaning old containers..."
docker compose down --remove-orphans

echo "🚀 Starting build (cached layers will speed up builds)..."
docker compose build

echo "🧩 Starting services..."
docker compose up -d

echo "🔍 Checking backend health..."
sleep 5
if curl -s http://localhost:8000/docs > /dev/null; then
  echo "✅ Backend is up at http://localhost:8000"
else
  echo "❌ Backend not responding on port 8000"
fi

echo "🔍 Checking frontend health..."
sleep 3
if curl -s http://localhost:8501 > /dev/null; then
  echo "✅ Frontend is up at http://localhost:8501"
else
  echo "❌ Frontend not responding on port 8501"
fi

echo "✅ Local test completed."
