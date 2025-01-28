import logging
from celery import Celery
import os
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
import tempfile

logger = logging.getLogger(__name__)


celery_app = Celery('preswald',
                    broker='redis://localhost:6379/0',
                    backend='redis://localhost:6379/0')

# Configure Celery to use our logger
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
    worker_hijack_root_logger=False,  # Don't hijack root logger
    worker_redirect_stdouts=False,    # Don't redirect stdout/stderr
)

# Get IPC file path from environment
def get_ipc_file():
    return os.environ.get("PRESWALD_IPC_FILE")

def write_to_ipc(data):
    """Write data to IPC file"""
    ipc_file = get_ipc_file()
    if not ipc_file:
        logger.warning("[Celery] No IPC file path set, skipping IPC write")
        return
        
    try:
        with open(ipc_file, 'w') as f:
            json.dump(data, f)
        logger.info("[Celery] Successfully wrote to IPC file: %s", ipc_file)
    except Exception as e:
        logger.error("[Celery] Error writing to IPC file: %s", str(e))

# Get script path from environment
def get_script_path():
    script_path = os.environ.get("SCRIPT_PATH")
    logger.info("[Celery] Getting script path from environment: %s", script_path)
    if not script_path:
        logger.warning("[Celery] No SCRIPT_PATH set in environment")
        return None
    return script_path

@celery_app.task(bind=True, name='preswald.parse_connections')
def parse_connections_task(self):
    """Celery task to parse all connections"""
    logger.info("[Celery] ====== Starting connection parsing task ======")
    logger.info("[Celery] Task ID: %s", self.request.id)
    
    try:
        connection_list = []
        
        # Add active connections
        from preswald.core import connections
        logger.info("[Celery] Found %d active connections in core", len(connections))
        logger.info("[Celery] Active connections keys: %s", list(connections.keys()))
        
        for name, conn in connections.items():
            try:
                conn_type = type(conn).__name__
                logger.info("[Celery] Processing active connection: %s (Type: %s)", name, conn_type)
                
                conn_info = {
                    "name": name,
                    "type": conn_type,
                    "details": str(conn)[:100] + "..." if len(str(conn)) > 100 else str(conn),
                    "status": "active",
                    "metadata": {}
                }
                connection_list.append(conn_info)
                logger.info("[Celery] Successfully added active connection: %s", name)
                logger.debug("[Celery] Connection details: %s", conn_info)
            except Exception as e:
                logger.error("[Celery] Error processing active connection %s: %s", name, str(e), exc_info=True)
                continue

        script_path = get_script_path()
        logger.info("[Celery] ====== Processing script ======")
        logger.info("[Celery] Script path from environment: %s", script_path)
        logger.info("[Celery] Script exists: %s", os.path.exists(script_path) if script_path else False)
        
        if script_path and os.path.exists(script_path):
            try:
                with open(script_path, 'r') as f:
                    script_content = f.read()
                logger.info("[Celery] Successfully read script content (%d characters)", len(script_content))

                script_dir = os.path.dirname(script_path)
                secrets_path = os.path.join(script_dir, "secrets.toml")
                logger.info("[Celery] Looking for secrets.toml at: %s", secrets_path)
                logger.info("[Celery] Secrets file exists: %s", os.path.exists(secrets_path))
                
                secrets = toml.load(secrets_path)
                openai_api_key = secrets.get('openai', {}).get('api_key')
                logger.info("[Celery] OpenAI API key found: %s", bool(openai_api_key))
                
                if not openai_api_key:
                    raise ValueError("OpenAI API key not found in secrets.toml")

                from preswald.llm import OpenAIService
                llm = OpenAIService(api_key=openai_api_key)
                logger.info("[Celery] Successfully initialized OpenAI service")
                
                logger.info("[Celery] ====== Starting LLM Analysis ======")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    logger.info("[Celery] Calling GPT API to analyze script")
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
                    logger.info("[Celery] Successfully received LLM response")
                    logger.debug("[Celery] LLM raw response: %s", llm_response)
                finally:
                    loop.close()
                    logger.info("[Celery] Closed asyncio loop")

                # Parse the LLM response
                logger.info("[Celery] ====== Processing LLM Results ======")
                llm_connections = json.loads(llm_response.arguments).get('connections', [])
                logger.info("[Celery] Found %d connections in LLM analysis", len(llm_connections))
                
                for conn in llm_connections:
                    logger.info("[Celery] Processing LLM-detected connection: %s (Type: %s)", 
                              conn.get("name"), conn.get("type"))
                    conn_info = {
                        "name": conn["name"],
                        "type": conn["type"],
                        "details": conn["details"],
                        "status": "detected",
                        "metadata": {"source": "llm_analysis"}
                    }
                    connection_list.append(conn_info)
                    logger.info("[Celery] Added LLM-detected connection: %s", conn["name"])

            except Exception as e:
                logger.error("[Celery] Error in LLM analysis: %s", str(e), exc_info=True)
            
        if script_path:
            try:
                logger.info("[Celery] ====== Processing preswald.toml ======")
                script_dir = os.path.dirname(script_path)
                config_path = os.path.join(script_dir, "preswald.toml")
                secrets_path = os.path.join(script_dir, "secrets.toml")
                
                logger.info("[Celery] Config path: %s", config_path)
                logger.info("[Celery] Config exists: %s", os.path.exists(config_path))
                logger.info("[Celery] Secrets exists: %s", os.path.exists(secrets_path))
                
                if os.path.exists(config_path):
                    config = toml.load(config_path)
                    logger.info("[Celery] Successfully loaded preswald.toml")
                    logger.info("[Celery] Config sections: %s", list(config.keys()))
                    
                    secrets = {}
                    if os.path.exists(secrets_path):
                        secrets = toml.load(secrets_path)
                        logger.info("[Celery] Successfully loaded secrets.toml")
                    
                    # Extract data connections
                    if "data" in config:
                        logger.info("[Celery] Found 'data' section in config")
                        logger.info("[Celery] Data connections found: %s", list(config["data"].keys()))
                        
                        for key, value in config["data"].items():
                            logger.info("[Celery] Processing config connection: %s", key)
                            logger.debug("[Celery] Connection config: %s", value)
                            
                            if not isinstance(value, dict):
                                logger.warning("[Celery] Skipping non-dict connection config: %s", key)
                                continue
                                
                            try:
                                conn_type = ""
                                details = {}
                                metadata = {}
                                
                                # PostgreSQL Connection
                                if all(field in value for field in ["host", "port", "dbname"]) and value.get("port") == 5432:
                                    logger.info("[Celery] Detected PostgreSQL connection: %s", key)
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
                                    logger.info("[Celery] Detected CSV connection: %s", key)
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
                                    logger.info("[Celery] Successfully added configured connection: %s (%s)", 
                                              key, conn_type)
                                    logger.debug("[Celery] Connection details: %s", conn_info)
                                    
                            except Exception as e:
                                logger.error("[Celery] Error processing connection %s: %s", 
                                           key, str(e), exc_info=True)
                                if conn_type:
                                    conn_info = {
                                        "name": key,
                                        "type": conn_type,
                                        "details": ", ".join(f"{k}: {v}" for k, v in details.items() if v),
                                        "status": "configured",
                                        "metadata": {"error": str(e)}
                                    }
                                    connection_list.append(conn_info)
                                    logger.info("[Celery] Added connection with error: %s", key)
            
            except Exception as e:
                logger.error("[Celery] Error reading config files: %s", str(e), exc_info=True)
                raise

        # Prepare result
        logger.info("[Celery] ====== Preparing Final Result ======")
        logger.info("[Celery] Total connections found: %d", len(connection_list))
        result = {
            "connections": connection_list,
            "error": None,
            "timestamp": time.time(),
            "is_parsing": False
        }
        logger.info("[Celery] Result prepared with %d connections", len(connection_list))
        logger.debug("[Celery] Full result: %s", result)
        
        # Write to IPC file
        write_to_ipc(result)
        logger.info("[Celery] ====== Task Complete ======")
        
        return result
        
    except Exception as e:
        logger.error("[Celery] ====== Task Failed ======")
        logger.error("[Celery] Error in connection parsing task: %s", str(e), exc_info=True)
        error_result = {
            "connections": [],
            "error": str(e),
            "timestamp": time.time(),
            "is_parsing": False
        }
        logger.info("[Celery] Writing error result to IPC file")
        write_to_ipc(error_result)
        return error_result