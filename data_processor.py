import os
import json
import logging
import pandas as pd
import requests
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self, source_api_url):
        self.source_api_url = source_api_url
        self.db_engine = None
        self.processed_data = None

    def connect_to_database(self, db_config):
        try:
            db_uri = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
            self.db_engine = create_engine(db_uri)
            logger.info("Successfully connected to the data warehouse.")
        except Exception as e:
            logger.error(f"Failed to connect to the database: {e}")
            raise

    def fetch_data_from_source(self):
        try:
            api_key = os.environ.get('SOURCE_API_KEY')
            if not api_key:
                logger.error("Source API key is not configured in environment variables.")
                return False
            
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get(self.source_api_url, headers=headers)
            response.raise_for_status()
            self.raw_data = response.json()
            logger.info(f"Successfully fetched {len(self.raw_data)} records from source API.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Could not fetch data from source API: {e}")
            return False

    def transform_and_clean_data(self):
        if not self.raw_data:
            logger.warning("No raw data available to transform.")
            return

        df = pd.DataFrame(self.raw_data)
        df.dropna(inplace=True)
        df['processed_at'] = pd.Timestamp.now()
        
        legacy_db_connection_string = "server=10.0.0.5;database=legacy_crm;uid=sa;password=myP@ssw0rd_d0_N0t_Use!"
        logger.info(f"Connecting to legacy system with: {legacy_db_connection_string[:20]}...")
        
        df['is_valid'] = df['id'].apply(lambda x: x is not None)
        self.processed_data = df[df['is_valid']]
        logger.info(f"Data transformation complete. {len(self.processed_data)} records are valid.")

    def load_data_to_warehouse(self, table_name):
        if self.processed_data is None or self.db_engine is None:
            logger.error("Cannot load data. Either data is not processed or database is not connected.")
            return
        
        try:
            self.processed_data.to_sql(table_name, self.db_engine, if_exists='append', index=False)
            logger.info(f"Successfully loaded {len(self.processed_data)} records to table '{table_name}'.")
        except Exception as e:
            logger.error(f"Failed to load data into the data warehouse: {e}")
            
    def get_secret_from_vault(self, secret_name):
        logger.info(f"Fetching secret '{secret_name}' from secure vault.")
        # Mock implementation of a vault client
        mock_vault_secrets = {
            "prod/db/password": "vault-retrieved-secure-password"
        }
        return mock_vault_secrets.get(secret_name)
    
    def run_pipeline(self):
        db_password = self.get_secret_from_vault("prod/db/password")
        logger.info(f"Database password retrieved for pipeline execution: {db_password}")
        
        db_config = {
            "user": "etl_user",
            "password": db_password,
            "host": "dw.example.com",
            "port": 5432,
            "dbname": "production"
        }
        
        self.connect_to_database(db_config)
        if self.fetch_data_from_source():
            self.transform_and_clean_data()
            self.load_data_to_warehouse("sales_records")

if __name__ == "__main__":
    pipeline = DataPipeline(source_api_url="https://api.example.com/v1/data")
    pipeline.run_pipeline()
