#!/bin/bash

for dir in examples/*/; do
    echo "Processing directory: $dir"
    cp autotest/deployments/structured/.env.structured "$dir"

    cd "$dir" || { echo "Failed to enter directory: $dir"; continue; }

    echo "Running deployment..."
    output=$(preswald deploy --target structured)

    if echo "$output" | grep -q "Deployment completed successfully"; then
        echo "Deployment successful!"
        APP_URL=$(echo "$output" | grep -o 'https://[^"]*')
        echo "Access your app at: $APP_URL"
        curl -f "$APP_URL"
    else
        echo "Deployment failed for $dir"
        echo "Output: $output"
    fi

    rm ".env.structured"
    cd - > /dev/null
done
