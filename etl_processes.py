import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import logging
import json
import os
from typing import Dict, List, Any
import requests
from faker import Faker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self, dbname: str, user: str, password: str, host: str = 'localhost', port: str = '5432'):
        self.connection_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }

    def connect(self):
        try:
            conn = psycopg2.connect(**self.connection_params)
            logger.info("Successfully connected to database")
            return conn
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise

class ETLProcess:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.fake = Faker()

    def extract_transactions(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Extract transaction data from source system"""
        try:
            # In a real implementation, this would connect to the actual source system
            # For demonstration, we'll generate synthetic data
            transactions = []
            for _ in range(1000):
                transaction = {
                    'transaction_id': self.fake.random_number(digits=8),
                    'transaction_date': self.fake.date_between(start_date=start_date, end_date=end_date),
                    'transaction_time': self.fake.time(),
                    'branch_id': self.fake.random_number(digits=4),
                    'customer_id': self.fake.random_number(digits=6),
                    'product_id': self.fake.random_number(digits=4),
                    'amount': round(self.fake.random_number(digits=4) + self.fake.random_number(digits=2) / 100, 2),
                    'transaction_type_id': self.fake.random_number(digits=2),
                    'employee_id': self.fake.random_number(digits=4),
                    'channel_id': self.fake.random_number(digits=2),
                    'status': self.fake.random_element(['COMPLETED', 'PENDING', 'FAILED'])
                }
                transactions.append(transaction)
            
            df = pd.DataFrame(transactions)
            logger.info(f"Extracted {len(df)} transactions")
            return df
        except Exception as e:
            logger.error(f"Error extracting transactions: {str(e)}")
            raise

    def extract_customers(self) -> pd.DataFrame:
        """Extract customer data from CRM system"""
        try:
            # In a real implementation, this would connect to the CRM API
            # For demonstration, we'll generate synthetic data
            customers = []
            for _ in range(500):
                customer = {
                    'customer_id': self.fake.random_number(digits=6),
                    'first_name': self.fake.first_name(),
                    'last_name': self.fake.last_name(),
                    'date_of_birth': self.fake.date_of_birth(minimum_age=18, maximum_age=90),
                    'address': self.fake.street_address(),
                    'city': self.fake.city(),
                    'state': self.fake.state(),
                    'zip_code': self.fake.zipcode(),
                    'email': self.fake.email(),
                    'phone': self.fake.phone_number(),
                    'customer_segment_id': self.fake.random_number(digits=2),
                    'acquisition_date': self.fake.date_between(start_date='-5y', end_date='today'),
                    'last_interaction_date': self.fake.date_time_between(start_date='-1y', end_date='now'),
                    'satisfaction_score': self.fake.random_int(min=0, max=10),
                    'nps_score': self.fake.random_int(min=0, max=10),
                    'status': self.fake.random_element(['ACTIVE', 'INACTIVE', 'PENDING'])
                }
                customers.append(customer)
            
            df = pd.DataFrame(customers)
            logger.info(f"Extracted {len(df)} customers")
            return df
        except Exception as e:
            logger.error(f"Error extracting customers: {str(e)}")
            raise

    def transform_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform transaction data"""
        try:
            # Convert date columns to datetime
            df['transaction_date'] = pd.to_datetime(df['transaction_date'])
            df['transaction_time'] = pd.to_datetime(df['transaction_time']).dt.time

            # Add derived columns
            df['is_weekend'] = df['transaction_date'].dt.dayofweek.isin([5, 6])
            df['is_holiday'] = df['transaction_date'].dt.dayofweek.isin([5, 6])  # Simplified holiday check

            # Validate data
            df = df[df['amount'] >= 0]  # Remove negative amounts
            df = df[df['status'].isin(['COMPLETED', 'PENDING', 'FAILED'])]

            logger.info(f"Transformed {len(df)} transactions")
            return df
        except Exception as e:
            logger.error(f"Error transforming transactions: {str(e)}")
            raise

    def transform_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform customer data"""
        try:
            # Convert date columns to datetime
            df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
            df['acquisition_date'] = pd.to_datetime(df['acquisition_date'])
            df['last_interaction_date'] = pd.to_datetime(df['last_interaction_date'])

            # Add derived columns
            df['age'] = (datetime.now() - df['date_of_birth']).dt.years
            df['customer_tenure_days'] = (datetime.now() - df['acquisition_date']).dt.days

            # Validate data
            df = df[df['satisfaction_score'].between(0, 10)]
            df = df[df['nps_score'].between(0, 10)]

            logger.info(f"Transformed {len(df)} customers")
            return df
        except Exception as e:
            logger.error(f"Error transforming customers: {str(e)}")
            raise

    def load_transactions(self, df: pd.DataFrame):
        """Load transformed transaction data into warehouse"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            # Insert into staging table
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO staging.transactions (
                        transaction_id, transaction_date, transaction_time,
                        branch_id, customer_id, product_id, amount,
                        transaction_type_id, employee_id, channel_id,
                        status, is_weekend, is_holiday
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (transaction_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        last_updated = CURRENT_TIMESTAMP
                """, (
                    row['transaction_id'], row['transaction_date'], row['transaction_time'],
                    row['branch_id'], row['customer_id'], row['product_id'], row['amount'],
                    row['transaction_type_id'], row['employee_id'], row['channel_id'],
                    row['status'], row['is_weekend'], row['is_holiday']
                ))

            conn.commit()
            logger.info(f"Loaded {len(df)} transactions")
        except Exception as e:
            logger.error(f"Error loading transactions: {str(e)}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def load_customers(self, df: pd.DataFrame):
        """Load transformed customer data into warehouse"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            # Insert into staging table
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO staging.customers (
                        customer_id, first_name, last_name, date_of_birth,
                        address, city, state, zip_code, email, phone,
                        customer_segment_id, acquisition_date, last_interaction_date,
                        satisfaction_score, nps_score, status, age, customer_tenure_days
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (customer_id) DO UPDATE SET
                        last_interaction_date = EXCLUDED.last_interaction_date,
                        satisfaction_score = EXCLUDED.satisfaction_score,
                        nps_score = EXCLUDED.nps_score,
                        status = EXCLUDED.status,
                        last_updated = CURRENT_TIMESTAMP
                """, (
                    row['customer_id'], row['first_name'], row['last_name'], row['date_of_birth'],
                    row['address'], row['city'], row['state'], row['zip_code'], row['email'],
                    row['phone'], row['customer_segment_id'], row['acquisition_date'],
                    row['last_interaction_date'], row['satisfaction_score'], row['nps_score'],
                    row['status'], row['age'], row['customer_tenure_days']
                ))

            conn.commit()
            logger.info(f"Loaded {len(df)} customers")
        except Exception as e:
            logger.error(f"Error loading customers: {str(e)}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def run_daily_etl(self):
        """Run daily ETL process"""
        try:
            logger.info("Starting daily ETL process")
            
            # Extract and transform transactions
            start_date = datetime.now() - timedelta(days=1)
            end_date = datetime.now()
            transactions_df = self.extract_transactions(start_date, end_date)
            transformed_transactions = self.transform_transactions(transactions_df)
            self.load_transactions(transformed_transactions)

            # Extract and transform customers
            customers_df = self.extract_customers()
            transformed_customers = self.transform_customers(customers_df)
            self.load_customers(transformed_customers)

            logger.info("Daily ETL process completed successfully")
        except Exception as e:
            logger.error(f"Error in daily ETL process: {str(e)}")
            raise

def main():
    # Initialize database connection
    db_connection = DatabaseConnection(
        dbname='bank_dw',
        user='postgres',
        password='your_password'  # In production, use environment variables
    )

    # Initialize ETL process
    etl = ETLProcess(db_connection)

    # Run daily ETL
    etl.run_daily_etl()

if __name__ == "__main__":
    main() 