#!/bin/bash
# Script para probar el Docker build localmente
cd /home/gcuevas/Railwaytestv3/backend

echo "🔨 Building Docker image..."
docker build -t tutorpaes-backend:test .

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful!"
    echo ""
    echo "To test the image with a local database, run:"
    echo "  docker run -e DATABASE_URL='postgresql+psycopg://user:pass@localhost:5432/db' -p 8000:8000 tutorpaes-backend:test"
else
    echo "❌ Docker build failed!"
    exit 1
fi
