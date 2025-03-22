import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import logging
import json
import os
from typing import Dict, List, Any, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_quality.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QualityCheckType(Enum):
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"
    TIMELINESS = "timeliness"

@dataclass
class QualityCheckResult:
    check_type: QualityCheckType
    table_name: str
    column_name: str
    check_date: datetime
    passed: bool
    details: Dict[str, Any]
    error_count: int
    total_count: int

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

class DataQualityChecker:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.results: List[QualityCheckResult] = []

    def check_completeness(self, table_name: str, column_name: str) -> QualityCheckResult:
        """Check for NULL values in a column"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            # Get total count and NULL count
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_count,
                    COUNT({column_name}) as non_null_count
                FROM {table_name}
            """)
            total_count, non_null_count = cursor.fetchone()

            # Calculate completeness percentage
            completeness = (non_null_count / total_count) * 100 if total_count > 0 else 0
            passed = completeness >= 95  # Threshold of 95%

            result = QualityCheckResult(
                check_type=QualityCheckType.COMPLETENESS,
                table_name=table_name,
                column_name=column_name,
                check_date=datetime.now(),
                passed=passed,
                details={
                    'completeness_percentage': completeness,
                    'null_count': total_count - non_null_count,
                    'non_null_count': non_null_count
                },
                error_count=total_count - non_null_count,
                total_count=total_count
            )

            logger.info(f"Completeness check for {table_name}.{column_name}: {completeness:.2f}%")
            return result

        except Exception as e:
            logger.error(f"Error in completeness check: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close()

    def check_accuracy(self, table_name: str, column_name: str, validation_rules: Dict[str, Any]) -> QualityCheckResult:
        """Check if values meet specified validation rules"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            # Build validation query based on rules
            validation_conditions = []
            for rule, value in validation_rules.items():
                if rule == 'min':
                    validation_conditions.append(f"{column_name} >= {value}")
                elif rule == 'max':
                    validation_conditions.append(f"{column_name} <= {value}")
                elif rule == 'allowed_values':
                    values = ", ".join(f"'{v}'" for v in value)
                    validation_conditions.append(f"{column_name} IN ({values})")

            validation_query = f"""
                SELECT 
                    COUNT(*) as total_count,
                    COUNT(CASE WHEN {' AND '.join(validation_conditions)} THEN 1 END) as valid_count
                FROM {table_name}
            """

            cursor.execute(validation_query)
            total_count, valid_count = cursor.fetchone()

            # Calculate accuracy percentage
            accuracy = (valid_count / total_count) * 100 if total_count > 0 else 0
            passed = accuracy >= 98  # Threshold of 98%

            result = QualityCheckResult(
                check_type=QualityCheckType.ACCURACY,
                table_name=table_name,
                column_name=column_name,
                check_date=datetime.now(),
                passed=passed,
                details={
                    'accuracy_percentage': accuracy,
                    'invalid_count': total_count - valid_count,
                    'valid_count': valid_count,
                    'validation_rules': validation_rules
                },
                error_count=total_count - valid_count,
                total_count=total_count
            )

            logger.info(f"Accuracy check for {table_name}.{column_name}: {accuracy:.2f}%")
            return result

        except Exception as e:
            logger.error(f"Error in accuracy check: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close()

    def check_consistency(self, table_name: str, column_name: str, reference_table: str, reference_column: str) -> QualityCheckResult:
        """Check referential integrity between tables"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            # Check for orphaned records
            cursor.execute(f"""
                SELECT COUNT(*) as orphaned_count
                FROM {table_name} t
                LEFT JOIN {reference_table} r ON t.{column_name} = r.{reference_column}
                WHERE r.{reference_column} IS NULL
            """)
            orphaned_count = cursor.fetchone()[0]

            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_count = cursor.fetchone()[0]

            # Calculate consistency percentage
            consistency = ((total_count - orphaned_count) / total_count) * 100 if total_count > 0 else 0
            passed = consistency == 100  # Must be 100% for referential integrity

            result = QualityCheckResult(
                check_type=QualityCheckType.CONSISTENCY,
                table_name=table_name,
                column_name=column_name,
                check_date=datetime.now(),
                passed=passed,
                details={
                    'consistency_percentage': consistency,
                    'orphaned_count': orphaned_count,
                    'reference_table': reference_table,
                    'reference_column': reference_column
                },
                error_count=orphaned_count,
                total_count=total_count
            )

            logger.info(f"Consistency check for {table_name}.{column_name}: {consistency:.2f}%")
            return result

        except Exception as e:
            logger.error(f"Error in consistency check: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close()

    def check_validity(self, table_name: str, column_name: str, data_type: str) -> QualityCheckResult:
        """Check if values match expected data type"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            # Build type validation query
            if data_type == 'numeric':
                validation_query = f"""
                    SELECT 
                        COUNT(*) as total_count,
                        COUNT(CASE WHEN {column_name} ~ '^[0-9]+\.?[0-9]*$' THEN 1 END) as valid_count
                    FROM {table_name}
                """
            elif data_type == 'date':
                validation_query = f"""
                    SELECT 
                        COUNT(*) as total_count,
                        COUNT(CASE WHEN {column_name}::date IS NOT NULL THEN 1 END) as valid_count
                    FROM {table_name}
                """
            else:
                raise ValueError(f"Unsupported data type: {data_type}")

            cursor.execute(validation_query)
            total_count, valid_count = cursor.fetchone()

            # Calculate validity percentage
            validity = (valid_count / total_count) * 100 if total_count > 0 else 0
            passed = validity == 100  # Must be 100% for data type validity

            result = QualityCheckResult(
                check_type=QualityCheckType.VALIDITY,
                table_name=table_name,
                column_name=column_name,
                check_date=datetime.now(),
                passed=passed,
                details={
                    'validity_percentage': validity,
                    'invalid_count': total_count - valid_count,
                    'valid_count': valid_count,
                    'data_type': data_type
                },
                error_count=total_count - valid_count,
                total_count=total_count
            )

            logger.info(f"Validity check for {table_name}.{column_name}: {validity:.2f}%")
            return result

        except Exception as e:
            logger.error(f"Error in validity check: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close()

    def check_timeliness(self, table_name: str, date_column: str, max_age_hours: int) -> QualityCheckResult:
        """Check if data is up to date"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            # Check for outdated records
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_count,
                    COUNT(CASE WHEN {date_column} >= NOW() - INTERVAL '{max_age_hours} hours' THEN 1 END) as recent_count
                FROM {table_name}
            """)
            total_count, recent_count = cursor.fetchone()

            # Calculate timeliness percentage
            timeliness = (recent_count / total_count) * 100 if total_count > 0 else 0
            passed = timeliness >= 95  # Threshold of 95%

            result = QualityCheckResult(
                check_type=QualityCheckType.TIMELINESS,
                table_name=table_name,
                column_name=date_column,
                check_date=datetime.now(),
                passed=passed,
                details={
                    'timeliness_percentage': timeliness,
                    'outdated_count': total_count - recent_count,
                    'recent_count': recent_count,
                    'max_age_hours': max_age_hours
                },
                error_count=total_count - recent_count,
                total_count=total_count
            )

            logger.info(f"Timeliness check for {table_name}.{date_column}: {timeliness:.2f}%")
            return result

        except Exception as e:
            logger.error(f"Error in timeliness check: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close()

    def run_quality_checks(self):
        """Run all quality checks"""
        try:
            logger.info("Starting data quality checks")

            # Define checks to run
            checks = [
                # Completeness checks
                (self.check_completeness, 'core.customer', 'email'),
                (self.check_completeness, 'core.customer', 'phone'),
                (self.check_completeness, 'core.transaction', 'amount'),

                # Accuracy checks
                (self.check_accuracy, 'core.customer', 'satisfaction_score', {'min': 0, 'max': 10}),
                (self.check_accuracy, 'core.customer', 'nps_score', {'min': 0, 'max': 10}),
                (self.check_accuracy, 'core.transaction', 'status', {'allowed_values': ['COMPLETED', 'PENDING', 'FAILED']}),

                # Consistency checks
                (self.check_consistency, 'core.transaction', 'customer_id', 'core.customer', 'customer_id'),
                (self.check_consistency, 'core.transaction', 'branch_id', 'core.branch', 'branch_id'),
                (self.check_consistency, 'core.transaction', 'product_id', 'core.product', 'product_id'),

                # Validity checks
                (self.check_validity, 'core.transaction', 'amount', 'numeric'),
                (self.check_validity, 'core.customer', 'date_of_birth', 'date'),
                (self.check_validity, 'core.transaction', 'transaction_date', 'date'),

                # Timeliness checks
                (self.check_timeliness, 'core.transaction', 'transaction_date', 24),
                (self.check_timeliness, 'core.customer', 'last_interaction_date', 30 * 24)
            ]

            # Run all checks
            for check_func, *args in checks:
                try:
                    result = check_func(*args)
                    self.results.append(result)
                    if not result.passed:
                        logger.warning(f"Quality check failed: {result.check_type.value} for {result.table_name}.{result.column_name}")
                except Exception as e:
                    logger.error(f"Error running check {check_func.__name__}: {str(e)}")

            # Generate quality report
            self.generate_quality_report()

            logger.info("Data quality checks completed")
        except Exception as e:
            logger.error(f"Error in quality checks: {str(e)}")
            raise

    def generate_quality_report(self):
        """Generate a quality report from check results"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'total_checks': len(self.results),
                'passed_checks': sum(1 for r in self.results if r.passed),
                'failed_checks': sum(1 for r in self.results if not r.passed),
                'check_details': []
            }

            for result in self.results:
                check_detail = {
                    'check_type': result.check_type.value,
                    'table_name': result.table_name,
                    'column_name': result.column_name,
                    'passed': result.passed,
                    'error_rate': (result.error_count / result.total_count) * 100 if result.total_count > 0 else 0,
                    'details': result.details
                }
                report['check_details'].append(check_detail)

            # Save report to file
            with open('quality_report.json', 'w') as f:
                json.dump(report, f, indent=4)

            logger.info("Quality report generated successfully")
        except Exception as e:
            logger.error(f"Error generating quality report: {str(e)}")
            raise

def main():
    # Initialize database connection
    db_connection = DatabaseConnection(
        dbname='bank_dw',
        user='postgres',
        password='your_password'  # In production, use environment variables
    )

    # Initialize quality checker
    quality_checker = DataQualityChecker(db_connection)

    # Run quality checks
    quality_checker.run_quality_checks()

if __name__ == "__main__":
    main() 