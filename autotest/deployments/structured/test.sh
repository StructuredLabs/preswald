#!/bin/bash

## Function to format time duration
format_time() {
    local seconds=$1
    printf "%02d:%02d:%02d" $((seconds/3600)) $((seconds%3600/60)) $((seconds%60))
}

# Function to print section headers
print_header() {
    echo "========================================="
    echo "$1"
    echo "========================================="
}

# Optional: Enable colors (comment out if not desired)
GREEN="\033[0;32m"
RED="\033[0;31m"
NC="\033[0m" # No Color

for dir in examples/*/; do
	print_header "Processing directory: $dir"

	start_time=$(date +%s)
    cp autotest/deployments/structured/.env.structured "$dir"
	end_time=$(date +%s)
	echo -e "${GREEN}[ OK ]${NC} Copied .env file [Time: $(format_time $((end_time - start_time)))]"

	cd "$dir" || { echo -e "${RED}[FAIL]${NC} Failed to enter directory: $dir"; continue; }

	# First deployment
	echo -e "\nRunning initial deployment..."
	start_time=$(date +%s)
    output=$(preswald deploy --target structured)
    end_time=$(date +%s)
    deploy_time=$((end_time - start_time))

    # CLOUD_RUN_URL=""
    PRESWALD_APP_URL=""
    
    if [[ "$output" == *"Starting production deployment"* ]]; then
		echo -e "${GREEN}[ OK ]${NC} Deployment successful! [Time: $(format_time $deploy_time)]"
        
        # Extract both URLs
        # CLOUD_RUN_URL=$(echo "$output" | grep -o 'https://.*\.a\.run\.app' | head -1)
        PRESWALD_APP_URL=$(echo "$output" | grep -o 'https://.*\.preswald\.app' | head -1)
        
        # If PRESWALD_APP_URL is empty, try to extract from the custom domain line
        if [ -z "$PRESWALD_APP_URL" ]; then
            DOMAIN=$(echo "$output" | grep 'Custom domain assigned at' | sed 's/.*Custom domain assigned at \(.*\)/\1/' | head -1)
            if [ ! -z "$DOMAIN" ]; then
                PRESWALD_APP_URL="https://$DOMAIN"
            fi
        fi
        
		# echo "   Cloud Run URL: $CLOUD_RUN_URL"
		echo "   Preswald App URL: $PRESWALD_APP_URL"

        # Check Cloud Run URL
        # if [ ! -z "$CLOUD_RUN_URL" ]; then
        #     start_time=$(date +%s)
        #     curl_output=$(curl -f "$CLOUD_RUN_URL" 2>/dev/null)
        #     curl_status=$?
        #     end_time=$(date +%s)
        #     
        #     if [ $curl_status -eq 0 ]; then
        #         echo -e "${GREEN}[ OK ]${NC} Verified Cloud Run URL accessibility [Time: $(format_time $((end_time - start_time)))]"
        #         echo "   Response preview:"
        #         echo "$curl_output" | head -5 | sed 's/^/     /'
        #     else
        #         echo -e "${RED}[FAIL]${NC} Could not access Cloud Run URL [Time: $(format_time $((end_time - start_time)))]"
        #     fi
        # else
        #     echo -e "${RED}[WARN]${NC} Could not extract Cloud Run URL from output"
        # fi
        
        # Check Preswald App URL
        if [ ! -z "$PRESWALD_APP_URL" ]; then
            start_time=$(date +%s)
            curl_output=$(curl -f "$PRESWALD_APP_URL" 2>/dev/null)
            curl_status=$?
            end_time=$(date +%s)
            
            if [ $curl_status -eq 0 ]; then
                echo -e "${GREEN}[ OK ]${NC} Verified Preswald App URL accessibility [Time: $(format_time $((end_time - start_time)))]"
                echo "   Response preview:"
                echo "$curl_output" | head -5 | sed 's/^/     /'
            else
                echo -e "${RED}[FAIL]${NC} Could not access Preswald App URL [Time: $(format_time $((end_time - start_time)))]"
            fi
        else
            echo -e "${RED}[WARN]${NC} Could not extract Preswald App URL from output"
        fi
    else
		echo -e "${RED}[FAIL]${NC} Deployment failed [Time: $(format_time $deploy_time)]"
        echo "   Output: $output"
    fi

	# Revision deployment
    echo -e "\nRevising deployment..."
    start_time=$(date +%s)
    output=$(preswald deploy --target structured)
    end_time=$(date +%s)
    revise_time=$((end_time - start_time))

    if [[ "$output" == *"Starting production deployment"* ]]; then
		echo -e "${GREEN}[ OK ]${NC} Revision successful! [Time: $(format_time $revise_time)]"
        
        # Extract both URLs
        # CLOUD_RUN_URL=$(echo "$output" | grep -o 'https://.*\.a\.run\.app' | head -1)
        PRESWALD_APP_URL=$(echo "$output" | grep -o 'https://.*\.preswald\.app' | head -1)
        
        # If PRESWALD_APP_URL is empty, try to extract from the custom domain line
        if [ -z "$PRESWALD_APP_URL" ]; then
            DOMAIN=$(echo "$output" | grep 'Custom domain assigned at' | sed 's/.*Custom domain assigned at \(.*\)/\1/' | head -1)
            if [ ! -z "$DOMAIN" ]; then
                PRESWALD_APP_URL="https://$DOMAIN"
            fi
        fi
        
		# echo "   Cloud Run URL: $CLOUD_RUN_URL"
		echo "   Preswald App URL: $PRESWALD_APP_URL"

        # Check Cloud Run URL
        # if [ ! -z "$CLOUD_RUN_URL" ]; then
        #     start_time=$(date +%s)
        #     curl_output=$(curl -f "$CLOUD_RUN_URL" 2>/dev/null)
        #     curl_status=$?
        #     end_time=$(date +%s)
        #     
        #     if [ $curl_status -eq 0 ]; then
        #         echo -e "${GREEN}[ OK ]${NC} Verified Cloud Run URL accessibility [Time: $(format_time $((end_time - start_time)))]"
        #         echo "   Response preview:"
        #         echo "$curl_output" | head -5 | sed 's/^/     /'
        #     else
        #         echo -e "${RED}[FAIL]${NC} Could not access Cloud Run URL [Time: $(format_time $((end_time - start_time)))]"
        #     fi
        # else
        #     echo -e "${RED}[WARN]${NC} Could not extract Cloud Run URL from output"
        # fi
        
        # Check Preswald App URL
        if [ ! -z "$PRESWALD_APP_URL" ]; then
            start_time=$(date +%s)
            curl_output=$(curl -f "$PRESWALD_APP_URL" 2>/dev/null)
            curl_status=$?
            end_time=$(date +%s)
            
            if [ $curl_status -eq 0 ]; then
                echo -e "${GREEN}[ OK ]${NC} Verified Preswald App URL accessibility [Time: $(format_time $((end_time - start_time)))]"
                echo "   Response preview:"
                echo "$curl_output" | head -5 | sed 's/^/     /'
            else
                echo -e "${RED}[FAIL]${NC} Could not access Preswald App URL [Time: $(format_time $((end_time - start_time)))]"
            fi
        else
            echo -e "${RED}[WARN]${NC} Could not extract Preswald App URL from output"
        fi
    else
		echo -e "${RED}[FAIL]${NC} Revision failed [Time: $(format_time $revise_time)]"
        echo "   Output: $output"
    fi

	# Stop deployment
    echo -e "\nStopping deployment..."
    start_time=$(date +%s)
    output=$(preswald stop --target structured)
    end_time=$(date +%s)
    stop_time=$((end_time - start_time))

    if [[ "$output" == *"Deployment stopped successfully"* ]]; then
        echo -e "${GREEN}[ OK ]${NC} Stop successful! [Time: $(format_time $stop_time)]"

        # Check both URLs are down
        start_time=$(date +%s)
        
        # Check Cloud Run URL is down
        # if [ ! -z "$CLOUD_RUN_URL" ]; then
        #     if curl -f "$CLOUD_RUN_URL" 2>/dev/null; then
        #         end_time=$(date +%s)
        #         echo -e "${RED}[FAIL]${NC} Error: Cloud Run URL still accessible [Check time: $(format_time $((end_time - start_time)))]"
        #         exit 1
        #     else
        #         end_time=$(date +%s)
        #         echo -e "${GREEN}[ OK ]${NC} Confirmed Cloud Run URL is down [Check time: $(format_time $((end_time - start_time)))]"
        #     fi
        # fi
        
        # Check Preswald App URL is down
        if [ ! -z "$PRESWALD_APP_URL" ]; then
            start_time=$(date +%s)
            if curl -f "$PRESWALD_APP_URL" 2>/dev/null; then
                end_time=$(date +%s)
                echo -e "${RED}[FAIL]${NC} Error: Preswald App URL still accessible [Check time: $(format_time $((end_time - start_time)))]"
                exit 1
            else
                end_time=$(date +%s)
                echo -e "${GREEN}[ OK ]${NC} Confirmed Preswald App URL is down [Check time: $(format_time $((end_time - start_time)))]"
            fi
        fi
    else
        echo -e "${RED}[FAIL]${NC} Stop failed [Time: $(format_time $stop_time)]"
        echo "   Output: $output"
    fi

    # Cleanup
    start_time=$(date +%s)
    rm ".env.structured"
    end_time=$(date +%s)
    echo -e "\n${GREEN}[ OK ]${NC} Cleaned up .env file [Time: $(format_time $((end_time - start_time)))]"

    cd - > /dev/null
    echo -e "\n"
done
