#!/bin/bash
# Quick deploy script for manual deployment
set -e

echo "🚀 Deploying frontend to Vercel..."
cd /workspaces/JANSETU/JANSETU/frontend
npm run build
npx vercel deploy --prod --confirm

echo ""
echo "🚀 Deploying backend to Render..."
echo "1. Go to: https://dashboard.render.com/new/blueprint"
echo "2. Select this repo and deploy using render.yaml"
echo "3. In Render service env vars, set values for:"
echo "   - SECRET_KEY"
echo "   - JWT_SECRET"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_SERVICE_KEY"
echo "4. Verify health endpoint: https://<render-service>.onrender.com/health"
echo ""
echo "✅ Frontend deployed. Backend deploy is configured and ready in Render blueprint."
