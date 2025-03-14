#!/bin/bash

GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m"

format_time() {
    local seconds=$1
    printf "%02d:%02d:%02d" $((seconds/3600)) $((seconds%3600/60)) $((seconds%60))
}

log() {
    local level=$1
    local message=$2
    local log_file=$3
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    case $level in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            echo "[$timestamp] [INFO] $message" >> "$log_file"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            echo "[$timestamp] [SUCCESS] $message" >> "$log_file"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message"
            echo "[$timestamp] [ERROR] $message" >> "$log_file"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            echo "[$timestamp] [WARNING] $message" >> "$log_file"
            ;;
        "DEBUG")
            echo -e "DEBUG: $message"
            echo "[$timestamp] [DEBUG] $message" >> "$log_file"
            ;;
    esac
}

test_example() {
    local dir=$1
    local project_name=$(basename "$dir")
    local log_file="${dir}/gcp_deployment_test.log"
    local test_failed=0
    
    if [[ "$project_name" == ".preswald_deploy" ]]; then
        return 0
    fi
    
    echo "================================================================="
    echo "Testing project: $project_name"
    echo "================================================================="
    
    echo "GCP Deployment Test for $project_name - $(date)" > "$log_file"
    echo "=================================================" >> "$log_file"
    
    log "INFO" "Starting GCP deployment test for $project_name" "$log_file"
    
    cd "$dir" || { 
        log "ERROR" "Failed to enter directory: $dir" "$log_file"
        return 1
    }
    
    log "INFO" "Deploying to GCP..." "$log_file"
    start_time=$(date +%s)
    
    echo "Running: preswald deploy --target gcp"
    if output=$(preswald deploy --target gcp 2>&1); then
        end_time=$(date +%s)
        deploy_time=$((end_time - start_time))
        
        log "DEBUG" "Full deployment output:" "$log_file"
        echo "----------------------------------------" >> "$log_file"
        echo "$output" >> "$log_file"
        echo "----------------------------------------" >> "$log_file"
        
        if echo "$output" | grep -i "error\|exception\|failed" > /dev/null; then
            log "ERROR" "Deployment command succeeded but output contains errors" "$log_file"
            log "DEBUG" "Error lines from output:" "$log_file"
            echo "$output" | grep -i "error\|exception\|failed" >> "$log_file"
            test_failed=1
        else
            log "SUCCESS" "Deployment successful! [Time: $(format_time $deploy_time)]" "$log_file"
            
            CLOUD_RUN_URL=$(echo "$output" | grep -o 'https://.*\.a\.run\.app' | head -1)
            
            if [ ! -z "$CLOUD_RUN_URL" ]; then
                log "INFO" "Cloud Run URL: $CLOUD_RUN_URL" "$log_file"
                
                log "INFO" "Testing deployed application..." "$log_file"
                start_time=$(date +%s)
                
                if curl_output=$(curl -s -f "$CLOUD_RUN_URL" 2>&1); then
                    end_time=$(date +%s)
                    log "SUCCESS" "Application is accessible [Time: $(format_time $((end_time - start_time)))]" "$log_file"
                    
                    log "DEBUG" "Response preview:" "$log_file"
                    echo "----------------------------------------" >> "$log_file"
                    echo "$curl_output" | head -10 >> "$log_file"
                    echo "----------------------------------------" >> "$log_file"
                else
                    end_time=$(date +%s)
                    log "ERROR" "Could not access deployed application [Time: $(format_time $((end_time - start_time)))]" "$log_file"
                    log "DEBUG" "Curl error:" "$log_file"
                    echo "----------------------------------------" >> "$log_file"
                    echo "$curl_output" >> "$log_file"
                    echo "----------------------------------------" >> "$log_file"
                    test_failed=1
                fi
            else
                log "ERROR" "Could not extract Cloud Run URL from output" "$log_file"
                log "DEBUG" "Searching output for deployment information..." "$log_file"
                echo "----------------------------------------" >> "$log_file"
                echo "$output" | grep -i "deploy\|url\|run\|service" >> "$log_file"
                echo "----------------------------------------" >> "$log_file"
                test_failed=1
            fi
        fi
        
        log "INFO" "Stopping GCP deployment..." "$log_file"
        start_time=$(date +%s)
        
        if stop_output=$(preswald stop --target gcp 2>&1); then
            end_time=$(date +%s)
            
            log "DEBUG" "Full stop output:" "$log_file"
            echo "----------------------------------------" >> "$log_file"
            echo "$stop_output" >> "$log_file"
            echo "----------------------------------------" >> "$log_file"
            
            if echo "$stop_output" | grep -i "error\|exception\|failed" > /dev/null; then
                log "ERROR" "Stop command succeeded but output contains errors" "$log_file"
                log "DEBUG" "Error lines from stop output:" "$log_file"
                echo "$stop_output" | grep -i "error\|exception\|failed" >> "$log_file"
                test_failed=1
            else
                log "SUCCESS" "Deployment stopped successfully [Time: $(format_time $((end_time - start_time)))]" "$log_file"
                
                if [ ! -z "$CLOUD_RUN_URL" ]; then
                    log "INFO" "Verifying app is no longer accessible..." "$log_file"
                    start_time=$(date +%s)
                    
                    if curl -s -f "$CLOUD_RUN_URL" > /dev/null 2>&1; then
                        end_time=$(date +%s)
                        log "ERROR" "Application is still accessible after cleanup [Time: $(format_time $((end_time - start_time)))]" "$log_file"
                        test_failed=1
                    else
                        end_time=$(date +%s)
                        log "SUCCESS" "Confirmed application is no longer accessible [Time: $(format_time $((end_time - start_time)))]" "$log_file"
                    fi
                fi
            fi
        else
            end_time=$(date +%s)
            log "ERROR" "Failed to stop deployment [Time: $(format_time $((end_time - start_time)))]" "$log_file"
            log "DEBUG" "Stop error output:" "$log_file"
            echo "----------------------------------------" >> "$log_file"
            echo "$stop_output" >> "$log_file"
            echo "----------------------------------------" >> "$log_file"
            test_failed=1
        fi
    else
        end_time=$(date +%s)
        deploy_time=$((end_time - start_time))
        log "ERROR" "Deployment failed [Time: $(format_time $deploy_time)]" "$log_file"
        log "DEBUG" "Deployment error output:" "$log_file"
        echo "----------------------------------------" >> "$log_file"
        echo "$output" >> "$log_file"
        echo "----------------------------------------" >> "$log_file"
        test_failed=1
    fi
    
    if [ $test_failed -eq 0 ]; then
        log "SUCCESS" "Test completed successfully, removing log file" "$log_file"
        rm "$log_file"
    else
        log "ERROR" "Test failed, keeping log file for debugging" "$log_file"
        echo -e "\nTest Failure Summary:" >> "$log_file"
        echo "----------------------------------------" >> "$log_file"
        grep -i "error\|exception\|failed" "$log_file" >> "$log_file"
        echo "----------------------------------------" >> "$log_file"
    fi
    
    cd - > /dev/null
    return $test_failed
}

echo "Starting GCP deployment tests for all example projects"
echo "================================================================="

example_dirs=$(find examples -maxdepth 1 -mindepth 1 -type d ! -name ".preswald_deploy")

failed_tests=0
failed_projects=()
for dir in $example_dirs; do
    test_example "$dir"
    if [ $? -eq 1 ]; then
        ((failed_tests++))
        failed_projects+=("$(basename "$dir")")
    fi
done

if [ $failed_tests -eq 0 ]; then
    echo -e "\n${GREEN}All tests completed successfully!${NC}"
    exit 0
else
    echo -e "\n${RED}${failed_tests} test(s) failed in the following projects:${NC}"
    for project in "${failed_projects[@]}"; do
        echo "- $project"
    done
    echo -e "\n${YELLOW}Check the following log files for details:${NC}"
    find examples -maxdepth 2 -name "gcp_deployment_test.log" ! -path "*/\.preswald_deploy/*" -exec echo "- {}" \;
    exit 1
fi