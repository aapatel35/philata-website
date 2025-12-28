#!/bin/bash

# Philata Social Media Automation - Run Script
# Usage: ./run.sh [command]
#
# Commands:
#   test-all       - Test posting to all platforms
#   test-instagram - Test Instagram posting
#   test-facebook  - Test Facebook posting
#   test-x         - Test X/Twitter posting
#   test-linkedin  - Test LinkedIn posting
#   docker         - Run in Docker container
#   docker-build   - Build Docker image
#   install        - Install dependencies

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables if .env exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
elif [ -f "../.env" ]; then
    export $(grep -v '^#' ../.env | xargs)
elif [ -f "../../.env" ]; then
    export $(grep -v '^#' ../../.env | xargs)
fi

case "$1" in
    test-all)
        echo "Testing all platforms..."
        python philata_social_poster.py test-all
        ;;
    test-instagram)
        echo "Testing Instagram..."
        python philata_social_poster.py test-instagram
        ;;
    test-facebook)
        echo "Testing Facebook..."
        python philata_social_poster.py test-facebook
        ;;
    test-x)
        echo "Testing X/Twitter..."
        python philata_social_poster.py test-x
        ;;
    test-linkedin)
        echo "Testing LinkedIn..."
        python philata_social_poster.py test-linkedin
        ;;
    docker)
        echo "Running in Docker..."
        docker-compose -f ../docker-compose.yml run --rm social-automation python philata_social_poster.py ${@:2}
        ;;
    docker-build)
        echo "Building Docker image..."
        docker-compose -f ../docker-compose.yml build social-automation
        ;;
    install)
        echo "Installing dependencies..."
        pip install -r requirements.txt
        ;;
    *)
        echo "Philata Social Media Automation"
        echo "================================"
        echo ""
        echo "Usage: ./run.sh [command]"
        echo ""
        echo "Commands:"
        echo "  test-all       - Test posting to all platforms"
        echo "  test-instagram - Test Instagram posting"
        echo "  test-facebook  - Test Facebook posting"
        echo "  test-x         - Test X/Twitter posting"
        echo "  test-linkedin  - Test LinkedIn posting"
        echo "  docker         - Run in Docker container"
        echo "  docker-build   - Build Docker image"
        echo "  install        - Install dependencies"
        echo ""
        echo "Example with Docker:"
        echo "  ./run.sh docker test-all"
        ;;
esac
