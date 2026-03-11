PROJECT_DIR="$HOME/project"
ARCHIVE_DIR="$PROJECT_DIR/archive"
MANIFESTS_DIR="$PROJECT_DIR/manifests"

mkdir -p "$ARCHIVE_DIR"
mkdir -p "$MANIFESTS_DIR"

echo "Stopping local API if running..."
pkill -f uvicorn || true

echo "Archiving old helper and duplicate files..."
[ -f "$PROJECT_DIR/fix.sh" ] && mv "$PROJECT_DIR/fix.sh" "$ARCHIVE_DIR/"
[ -f "$PROJECT_DIR/demo-app-stress.yaml" ] && mv "$PROJECT_DIR/demo-app-stress.yaml" "$ARCHIVE_DIR/"

echo "Archiving old demo-app manifests if present..."
[ -f "$MANIFESTS_DIR/demo-app-deployment.yaml" ] && mv "$MANIFESTS_DIR/demo-app-deployment.yaml" "$ARCHIVE_DIR/"
[ -f "$MANIFESTS_DIR/demo-app-hpa.yaml" ] && mv "$MANIFESTS_DIR/demo-app-hpa.yaml" "$ARCHIVE_DIR/"

echo "Removing old nested virtualenv..."
rm -rf "$PROJECT_DIR/demo-app/venv"

echo "Removing Python caches..."
find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + || true

echo "Deleting old demo-app kubernetes resources if they exist..."
kubectl delete hpa demo-hpa --ignore-not-found
kubectl delete hpa demo-app-hpa --ignore-not-found
kubectl delete deployment demo-app --ignore-not-found

echo "Showing final structure..."
echo
find "$PROJECT_DIR" -maxdepth 3 | sort
echo
echo "Cleanup complete."
echo "Archived files are in: $ARCHIVE_DIR"
