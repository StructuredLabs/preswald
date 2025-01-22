from celery import Celery
import os
import logging
import toml
import psycopg2
from sqlalchemy import create_engine, inspect
import pandas as pd
from urllib.parse import quote_plus
import requests
from io import StringIO
import time
import json
import asyncio

logger = logging.getLogger(__name__)

celery_app = Celery('preswald',
                    broker='redis://localhost:6379/0',
                    backend='redis://localhost:6379/0')

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600, 
    worker_prefetch_multiplier=1, 
    worker_max_tasks_per_child=1000,
)

@celery_app.task(bind=True, name='preswald.parse_connections')
def parse_connections_task(self):
    """Celery task to parse all connections"""
    logger.info("[Celery] Starting connection parsing task")
    
    # Import globals from server
    from preswald.server import connections_cache, connections_parsing_status
    
    try:
        connections_parsing_status["is_parsing"] = True
        connections_parsing_status["error"] = None
        connection_list = []
        
        # Add active connections
        from preswald.core import connections
        for name, conn in connections.items():
            try:
                conn_type = type(conn).__name__
                conn_info = {
                    "name": name,
                    "type": conn_type,
                    "details": str(conn)[:100] + "..." if len(str(conn)) > 100 else str(conn),
                    "status": "active",
                    "metadata": {}
                }
                connection_list.append(conn_info)
            except Exception as e:
                logger.error(f"Error processing active connection {name}: {e}")
                continue

        # Get script path
        from preswald.server import SCRIPT_PATH
        if SCRIPT_PATH and os.path.exists(SCRIPT_PATH):
            try:
                # Read the script content
                with open(SCRIPT_PATH, 'r') as f:
                    script_content = f.read()

                # Get OpenAI API key from secrets.toml
                script_dir = os.path.dirname(SCRIPT_PATH)
                secrets_path = os.path.join(script_dir, "secrets.toml")
                secrets = toml.load(secrets_path)
                openai_api_key = secrets.get('openai', {}).get('api_key')
                
                if not openai_api_key:
                    raise ValueError("OpenAI API key not found in secrets.toml")

                # Initialize OpenAI service
                from preswald.llm import OpenAIService
                llm = OpenAIService(api_key=openai_api_key)
                
                # Call LLM to analyze connections using asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    llm_response = loop.run_until_complete(llm.call_gpt_api_non_streamed(
                        text=f"Below is a python code. Please go through the code and give me the file or data connections that are being made/created in the code.\n\n{script_content}",
                        model=llm.GPT_4_TURBO,
                        sys_prompt=llm.ASSISTANT_SYS_PROMPT,
                        response_type="json_object",
                        tools=[
                            {
                                "type": "function",
                                "function": {
                                    "name": "extract_connections",
                                    "description": "Extract the file or data connections that are being made/created in the code",
                                    "parameters": {
                                        "type": "object",
                                        "properties": {
                                            "connections": {
                                                "type": "array",
                                                "description": "The connections that are being made/created in the code",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {
                                                            "type": "string",
                                                            "description": "The name of the connection"
                                                        },
                                                        "type": {
                                                            "type": "string", 
                                                            "description": "The type of the connection"
                                                        },
                                                        "details": {
                                                            "type": "string",
                                                            "description": "Additional details about the connection"
                                                        }
                                                    },
                                                    "required": ["name", "type", "details"]
                                                }
                                            }
                                        },
                                        "required": ["connections"]
                                    }
                                }
                            }
                        ],
                        tool_choice={
                            "type": "function",
                            "function": {"name": "extract_connections"}
                        }
                    ))
                finally:
                    loop.close()

                # Parse the LLM response and add to connection list
                llm_connections = json.loads(llm_response.arguments).get('connections', [])
                for conn in llm_connections:
                    conn_info = {
                        "name": conn["name"],
                        "type": conn["type"],
                        "details": conn["details"],
                        "status": "detected",
                        "metadata": {"source": "llm_analysis"}
                    }
                    connection_list.append(conn_info)

            except Exception as e:
                logger.error(f"Error analyzing script with LLM: {str(e)}")
            
        if SCRIPT_PATH:
            try:
                script_dir = os.path.dirname(SCRIPT_PATH)
                config_path = os.path.join(script_dir, "config.toml")
                secrets_path = os.path.join(script_dir, "secrets.toml")
                
                if os.path.exists(config_path):
                    config = toml.load(config_path)
                    secrets = {}
                    if os.path.exists(secrets_path):
                        secrets = toml.load(secrets_path)
                    
                    # Extract data connections
                    if "data" in config:
                        for key, value in config["data"].items():
                            if not isinstance(value, dict):
                                continue
                                
                            try:
                                conn_type = ""
                                details = {}
                                metadata = {}
                                
                                # PostgreSQL Connection
                                if all(field in value for field in ["host", "port", "dbname"]) and value.get("port") == 5432:
                                    conn_type = "PostgreSQL"
                                    details = {
                                        "host": value.get("host", ""),
                                        "port": value.get("port", ""),
                                        "dbname": value.get("dbname", ""),
                                        "user": value.get("user", "")
                                    }
                                    
                                    # Get PostgreSQL metadata
                                    try:
                                        password = None
                                        secret_key = f"{key}"
                                        logger.info(f"Looking for password with key: {secret_key} {secrets}")
                                        if secret_key in secrets['data']:
                                            password = secrets['data'][secret_key].get("password")
                                            if password:
                                                logger.info(f"Found password in secrets.toml for {key}")
                                            else:
                                                logger.warning(f"Password field is empty in secrets.toml for {key}")
                                                metadata = {"error": "Password field is empty in secrets.toml"}
                                                continue
                                        else:
                                            logger.warning(f"No password entry found in secrets.toml for {key}")
                                            metadata = {"error": "No password entry found in secrets.toml"}
                                            continue

                                        if password:
                                            password = quote_plus(password)
                                            conn_str = f"postgresql://{details['user']}:{password}@{details['host']}:{details['port']}/{details['dbname']}"
                                            
                                            engine = create_engine(conn_str)
                                            with engine.connect() as connection:
                                                inspector = inspect(engine)
                                                schemas = inspector.get_schema_names()
                                                tables_info = {}
                                                
                                                for schema in schemas:
                                                    tables = inspector.get_table_names(schema=schema)
                                                    tables_info[schema] = {}
                                                    
                                                    for table in tables:
                                                        columns = inspector.get_columns(table, schema=schema)
                                                        tables_info[schema][table] = {
                                                            "columns": [
                                                                {
                                                                    "name": col["name"],
                                                                    "type": str(col["type"]),
                                                                    "nullable": col["nullable"]
                                                                }
                                                                for col in columns
                                                            ]
                                                        }
                                                
                                                metadata = {
                                                    "database_name": details["dbname"],
                                                    "schemas": tables_info,
                                                    "total_tables": sum(len(tables) for tables in tables_info.values())
                                                }
                                                logger.info(f"Successfully connected to PostgreSQL database for {key}")
                                    except Exception as e:
                                        error_msg = str(e)
                                        logger.warning(f"Could not fetch PostgreSQL metadata: {error_msg}")
                                        if "password" in error_msg.lower():
                                            metadata = {"error": "Invalid password. Please check your credentials in secrets.toml"}
                                        else:
                                            metadata = {"error": f"Could not connect to database: {error_msg}"}
                                
                                # CSV Connection
                                elif "path" in value and str(value["path"]).endswith(".csv"):
                                    conn_type = "CSV"
                                    file_path = value.get("path", "")
                                    details = {"path": file_path}
                                    
                                    try:
                                        if file_path.startswith(("http://", "https://")):
                                            response = requests.get(file_path)
                                            response.raise_for_status()
                                            
                                            csv_content = StringIO(response.text)
                                            df = pd.read_csv(csv_content, nrows=5)
                                            
                                            total_rows = len(response.text.splitlines()) - 1
                                            file_size_mb = len(response.content) / (1024*1024)
                                            
                                            metadata = {
                                                "columns": [
                                                    {
                                                        "name": col,
                                                        "type": str(df[col].dtype),
                                                        "sample_values": [str(val) for val in df[col].head().tolist()]
                                                    }
                                                    for col in df.columns
                                                ],
                                                "total_rows": total_rows,
                                                "total_columns": len(df.columns),
                                                "file_size": f"{file_size_mb:.2f} MB",
                                                "source": "remote"
                                            }
                                            logger.info(f"Successfully read remote CSV file: {file_path}")
                                            
                                        else:
                                            if file_path.startswith("./"):
                                                file_path = os.path.join(script_dir, file_path[2:])
                                                
                                            if os.path.exists(file_path):
                                                df = pd.read_csv(file_path, nrows=5)
                                                total_rows = sum(1 for _ in open(file_path)) - 1
                                                file_size_mb = os.path.getsize(file_path) / (1024*1024)
                                                
                                                metadata = {
                                                    "columns": [
                                                        {
                                                            "name": col,
                                                            "type": str(df[col].dtype),
                                                            "sample_values": [str(val) for val in df[col].head().tolist()]
                                                        }
                                                        for col in df.columns
                                                    ],
                                                    "total_rows": total_rows,
                                                    "total_columns": len(df.columns),
                                                    "file_size": f"{file_size_mb:.2f} MB",
                                                    "source": "local"
                                                }
                                                logger.info(f"Successfully read local CSV file: {file_path}")
                                            else:
                                                metadata = {"error": "File not found", "source": "local"}
                                    except requests.exceptions.RequestException as e:
                                        logger.warning(f"Could not fetch remote CSV file: {str(e)}")
                                        metadata = {"error": f"Could not fetch remote file: {str(e)}", "source": "remote"}
                                    except Exception as e:
                                        logger.warning(f"Could not read CSV metadata: {str(e)}")
                                        metadata = {"error": f"Could not read file: {str(e)}", "source": "unknown"}
                                
                                if conn_type:
                                    conn_info = {
                                        "name": key,
                                        "type": conn_type,
                                        "details": ", ".join(f"{k}: {v}" for k, v in details.items() if v),
                                        "status": "configured",
                                        "metadata": metadata
                                    }
                                    connection_list.append(conn_info)
                                    
                            except Exception as e:
                                logger.error(f"Error processing connection {key}: {str(e)}")
                                if conn_type:
                                    conn_info = {
                                        "name": key,
                                        "type": conn_type,
                                        "details": ", ".join(f"{k}: {v}" for k, v in details.items() if v),
                                        "status": "configured",
                                        "metadata": {"error": str(e)}
                                    }
                                    connection_list.append(conn_info)
            
            except Exception as e:
                logger.error(f"Error reading config files: {str(e)}")
                raise

        # Update the cache with parsed connections
        connections_cache["connections"] = connection_list
        connections_parsing_status["last_parsed"] = time.time()
        
    except Exception as e:
        logger.error(f"Error in connection parsing task: {str(e)}")
        connections_parsing_status["error"] = str(e)
    finally:
        connections_parsing_status["is_parsing"] = False
        
    return {
        "connections": connection_list,
        "error": connections_parsing_status["error"],
        "timestamp": connections_parsing_status["last_parsed"]
    }