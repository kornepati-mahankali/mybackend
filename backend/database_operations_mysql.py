import os
import mysql.connector
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EProcurementDBMySQL:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '3307'))
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'toolinformation')
    
    def get_connection(self):
        """Get MySQL database connection"""
        try:
            return mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False
            )
        except Exception as e:
            logger.error(f"MySQL connection error: {e}")
            raise
    
    def create_table_if_not_exists(self):
        """Create the eprocurement_tenders table if it doesn't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS eprocurement_tenders (
                id VARCHAR(36) PRIMARY KEY,
                bid_user VARCHAR(100),
                tender_id VARCHAR(100),
                name_of_work TEXT,
                tender_category VARCHAR(50),
                department VARCHAR(100),
                quantity VARCHAR(50),
                emd DECIMAL(15, 2),
                exemption VARCHAR(50),
                ecv DECIMAL(20, 2),
                state_name VARCHAR(100),
                location VARCHAR(100),
                apply_mode VARCHAR(50),
                website VARCHAR(100),
                document_link TEXT,
                closing_date DATE,
                pincode VARCHAR(10),
                attachments TEXT,
                source_session_id VARCHAR(100),
                source_file VARCHAR(255),
                merge_session_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_tender_id (tender_id),
                INDEX idx_merge_session (merge_session_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            logger.info("eprocurement_tenders table created/verified successfully")
            
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def store_merged_data(self, df: pd.DataFrame, merge_session_id: str, source_session_id: str = None, source_file: str = None) -> Dict[str, Any]:
        """
        Store merged e-procurement data in the MySQL database
        
        Args:
            df: Pandas DataFrame containing the merged data
            merge_session_id: Unique identifier for the merge operation
            source_session_id: Original session ID (optional)
            source_file: Original file name (optional)
        
        Returns:
            Dict containing operation results
        """
        conn = None
        cursor = None
        try:
            # Ensure table exists
            self.create_table_if_not_exists()
            
            # Debug: Log the DataFrame columns
            logger.info(f"DataFrame columns: {list(df.columns)}")
            logger.info(f"DataFrame shape: {df.shape}")
            logger.info(f"First few rows: {df.head().to_dict('records')}")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Prepare data for insertion
            records_inserted = 0
            records_skipped = 0
            records_updated = 0
            
            logger.info(f"Starting to process {len(df)} records for merge session {merge_session_id}")
            
            for index, row in df.iterrows():
                try:
                    # Clean and prepare data - handle different column name variations
                    tender_id = str(row.get('Tender ID', row.get('tender_id', row.get('TenderID', '')))).strip()
                    if not tender_id:  # Skip records without tender ID
                        records_skipped += 1
                        logger.warning(f"Row {index}: Skipping record without tender ID")
                        continue
                    
                    # Generate UUID for MySQL
                    import uuid
                    record_id = str(uuid.uuid4())
                    
                    # Check if tender already exists
                    cursor.execute(
                        "SELECT id FROM eprocurement_tenders WHERE tender_id = %s",
                        (tender_id,)
                    )
                    
                    existing_record = cursor.fetchone()
                    
                    if existing_record:
                        # Update existing record
                        cursor.execute("""
                            UPDATE eprocurement_tenders SET
                                bid_user = %s,
                                name_of_work = %s,
                                tender_category = %s,
                                department = %s,
                                quantity = %s,
                                emd = %s,
                                exemption = %s,
                                ecv = %s,
                                state_name = %s,
                                location = %s,
                                apply_mode = %s,
                                website = %s,
                                document_link = %s,
                                closing_date = %s,
                                pincode = %s,
                                attachments = %s,
                                source_session_id = %s,
                                source_file = %s,
                                merge_session_id = %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE tender_id = %s
                        """, (
                            str(row.get('Bid User', row.get('bid_user', ''))),
                            str(row.get('Name of Work', row.get('name_of_work', row.get('Name of Work', '')))),
                            str(row.get('Tender Category', row.get('tender_category', row.get('TenderCategory', '')))),
                            str(row.get('Department', row.get('department', ''))),
                            str(row.get('Quantity', row.get('quantity', ''))),
                            self._parse_decimal(row.get('EMD', row.get('emd', ''))),
                            str(row.get('Exemption', row.get('exemption', ''))),
                            self._parse_decimal(row.get('ECV', row.get('ecv', ''))),
                            str(row.get('State Name', row.get('state_name', row.get('StateName', '')))),
                            str(row.get('Location', row.get('location', ''))),
                            str(row.get('Apply Mode', row.get('apply_mode', row.get('ApplyMode', '')))),
                            str(row.get('Website', row.get('website', ''))),
                            str(row.get('Document Link', row.get('document_link', row.get('DocumentLink', '')))),
                            self._parse_date(row.get('Closing Date', row.get('closing_date', row.get('ClosingDate', '')))),
                            str(row.get('Pincode', row.get('pincode', ''))),
                            str(row.get('Attachments', row.get('attachments', ''))),
                            source_session_id,
                            source_file,
                            merge_session_id,
                            tender_id
                        ))
                        records_updated += 1
                        logger.info(f"Updated existing tender: {tender_id}")
                    else:
                        # Insert new record
                        cursor.execute("""
                            INSERT INTO eprocurement_tenders (
                                id, bid_user, tender_id, name_of_work, tender_category, department,
                                quantity, emd, exemption, ecv, state_name, location, apply_mode,
                                website, document_link, closing_date, pincode, attachments,
                                source_session_id, source_file, merge_session_id
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            record_id,
                            str(row.get('Bid User', row.get('bid_user', ''))),
                            tender_id,
                            str(row.get('Name of Work', row.get('name_of_work', row.get('Name of Work', '')))),
                            str(row.get('Tender Category', row.get('tender_category', row.get('TenderCategory', '')))),
                            str(row.get('Department', row.get('department', ''))),
                            str(row.get('Quantity', row.get('quantity', ''))),
                            self._parse_decimal(row.get('EMD', row.get('emd', ''))),
                            str(row.get('Exemption', row.get('exemption', ''))),
                            self._parse_decimal(row.get('ECV', row.get('ecv', ''))),
                            str(row.get('State Name', row.get('state_name', row.get('StateName', '')))),
                            str(row.get('Location', row.get('location', ''))),
                            str(row.get('Apply Mode', row.get('apply_mode', row.get('ApplyMode', '')))),
                            str(row.get('Website', row.get('website', ''))),
                            str(row.get('Document Link', row.get('document_link', row.get('DocumentLink', '')))),
                            self._parse_date(row.get('Closing Date', row.get('closing_date', row.get('ClosingDate', '')))),
                            str(row.get('Pincode', row.get('pincode', ''))),
                            str(row.get('Attachments', row.get('attachments', ''))),
                            source_session_id,
                            source_file,
                            merge_session_id
                        ))
                        records_inserted += 1
                        logger.info(f"Inserted new tender: {tender_id}")
                    
                except Exception as e:
                    logger.error(f"Error processing row {index}: {e}")
                    records_skipped += 1
                    continue
            
            conn.commit()
            logger.info(f"Database operation completed successfully. Inserted: {records_inserted}, Updated: {records_updated}, Skipped: {records_skipped}")
            
            return {
                'success': True,
                'records_inserted': records_inserted,
                'records_updated': records_updated,
                'records_skipped': records_skipped,
                'total_processed': len(df),
                'merge_session_id': merge_session_id
            }
            
        except Exception as e:
            logger.error(f"Database operation error: {e}")
            if conn:
                conn.rollback()
            return {
                'success': False,
                'error': str(e),
                'records_inserted': 0,
                'records_updated': 0,
                'records_skipped': 0
            }
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_merged_data(self, merge_session_id: str = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieve merged e-procurement data from MySQL database
        
        Args:
            merge_session_id: Filter by merge session ID (optional)
            limit: Number of records to return
            offset: Number of records to skip
        
        Returns:
            Dict containing data and metadata
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Build query
            query = "SELECT * FROM eprocurement_tenders"
            params = []
            
            if merge_session_id:
                query += " WHERE merge_session_id = %s"
                params.append(merge_session_id)
            
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            records = cursor.fetchall()
            
            # Get total count
            count_query = "SELECT COUNT(*) as total FROM eprocurement_tenders"
            if merge_session_id:
                count_query += " WHERE merge_session_id = %s"
                cursor.execute(count_query, [merge_session_id])
            else:
                cursor.execute(count_query)
            
            total_count = cursor.fetchone()['total']
            
            return {
                'success': True,
                'data': records,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f"Database retrieval error: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': [],
                'total_count': 0
            }
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def delete_merged_data(self, merge_session_id: str) -> Dict[str, Any]:
        """
        Delete merged data by merge session ID
        
        Args:
            merge_session_id: Merge session ID to delete
        
        Returns:
            Dict containing operation results
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM eprocurement_tenders WHERE merge_session_id = %s",
                (merge_session_id,)
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'merge_session_id': merge_session_id
            }
            
        except Exception as e:
            logger.error(f"Database deletion error: {e}")
            if conn:
                conn.rollback()
            return {
                'success': False,
                'error': str(e),
                'deleted_count': 0
            }
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def _parse_decimal(self, value) -> float:
        """Parse decimal values from string"""
        if pd.isna(value) or value == '':
            return None
        try:
            # Remove currency symbols and commas
            if isinstance(value, str):
                value = value.replace('₹', '').replace(',', '').replace(' ', '')
            return float(value) if value else None
        except:
            return None
    
    def _parse_date(self, value) -> str:
        """Parse date values from string"""
        if pd.isna(value) or value == '':
            return None
        try:
            if isinstance(value, str):
                # Try to parse common date formats
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%y']:
                    try:
                        parsed_date = datetime.strptime(value, fmt)
                        return parsed_date.strftime('%Y-%m-%d')
                    except:
                        continue
            return str(value) if value else None
        except:
            return None 