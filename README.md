#!/bin/bash

# ---------------------------------------------
# Script to install flexierp_custom_user_management on Frappe
# Author: amirmansouri.dev@gmail.com
# ---------------------------------------------

# CONFIGURATION
SITE_NAME="site1.local"
APP_NAME="flexierp_custom_user_management"
GIT_REPO="https://github.com/YOUR_USERNAME/flexierp_custom_user_management.git"  # <- UPDATE THIS

# STEP 1: Clone the app
echo "📦 Cloning app..."
cd apps || exit
if [ -d "$APP_NAME" ]; then
  echo "⚠️ App folder already exists. Skipping clone."
else
  git clone "$GIT_REPO"
fi

# STEP 2: Add app to bench
cd ..
echo "🔗 Adding app to bench..."
bench --site "$SITE_NAME" install-app "$APP_NAME"

# STEP 3: Run migrations
echo "🔄 Migrating site..."
bench --site "$SITE_NAME" migrate

# STEP 4: Restart bench
echo "🚀 Restarting Frappe..."
bench restart

echo "✅ Done! App '$APP_NAME' installed on site '$SITE_NAME'"
