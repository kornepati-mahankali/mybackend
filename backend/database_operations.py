import os
import psycopg2
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EProcurementDB:
    def __init__(self):
        self.connection_string = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/scraper_db')
    
    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(self.connection_string)
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def store_merged_data(self, df: pd.DataFrame, merge_session_id: str, source_session_id: str = None, source_file: str = None) -> Dict[str, Any]:
        """
        Store merged e-procurement data in the database
        
        Args:
            df: Pandas DataFrame containing the merged data
            merge_session_id: Unique identifier for the merge operation
            source_session_id: Original session ID (optional)
            source_file: Original file name (optional)
        
        Returns:
            Dict containing operation results
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Prepare data for insertion
            records_inserted = 0
            records_skipped = 0
            
            for _, row in df.iterrows():
                try:
                    # Clean and prepare data
                    tender_id = str(row.get('Tender ID', '')).strip()
                    if not tender_id:  # Skip records without tender ID
                        records_skipped += 1
                        continue
                    
                    # Check if tender already exists
                    cursor.execute(
                        "SELECT id FROM eprocurement_tenders WHERE tender_id = %s",
                        (tender_id,)
                    )
                    
                    if cursor.fetchone():
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
                                updated_at = NOW()
                            WHERE tender_id = %s
                        """, (
                            str(row.get('Bid User', '')),
                            str(row.get('Name of Work', '')),
                            str(row.get('Tender Category', '')),
                            str(row.get('Department', '')),
                            str(row.get('Quantity', '')),
                            self._parse_decimal(row.get('EMD', '')),
                            str(row.get('Exemption', '')),
                            self._parse_decimal(row.get('ECV', '')),
                            str(row.get('State Name', '')),
                            str(row.get('Location', '')),
                            str(row.get('Apply Mode', '')),
                            str(row.get('Website', '')),
                            str(row.get('Document Link', '')),
                            self._parse_date(row.get('Closing Date', '')),
                            str(row.get('Pincode', '')),
                            str(row.get('Attachments', '')),
                            source_session_id,
                            source_file,
                            merge_session_id,
                            tender_id
                        ))
                    else:
                        # Insert new record
                        cursor.execute("""
                            INSERT INTO eprocurement_tenders (
                                bid_user, tender_id, name_of_work, tender_category, department,
                                quantity, emd, exemption, ecv, state_name, location, apply_mode,
                                website, document_link, closing_date, pincode, attachments,
                                source_session_id, source_file, merge_session_id
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            str(row.get('Bid User', '')),
                            tender_id,
                            str(row.get('Name of Work', '')),
                            str(row.get('Tender Category', '')),
                            str(row.get('Department', '')),
                            str(row.get('Quantity', '')),
                            self._parse_decimal(row.get('EMD', '')),
                            str(row.get('Exemption', '')),
                            self._parse_decimal(row.get('ECV', '')),
                            str(row.get('State Name', '')),
                            str(row.get('Location', '')),
                            str(row.get('Apply Mode', '')),
                            str(row.get('Website', '')),
                            str(row.get('Document Link', '')),
                            self._parse_date(row.get('Closing Date', '')),
                            str(row.get('Pincode', '')),
                            str(row.get('Attachments', '')),
                            source_session_id,
                            source_file,
                            merge_session_id
                        ))
                    
                    records_inserted += 1
                    
                except Exception as e:
                    logger.error(f"Error processing row: {e}")
                    records_skipped += 1
                    continue
            
            conn.commit()
            
            return {
                'success': True,
                'records_inserted': records_inserted,
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
                'records_skipped': 0
            }
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_merged_data(self, merge_session_id: str = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieve merged e-procurement data from database
        
        Args:
            merge_session_id: Filter by merge session ID (optional)
            limit: Number of records to return
            offset: Number of records to skip
        
        Returns:
            Dict containing data and metadata
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
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
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Convert to list of dictionaries
            data = []
            for record in records:
                data.append(dict(zip(columns, record)))
            
            # Get total count
            count_query = "SELECT COUNT(*) FROM eprocurement_tenders"
            if merge_session_id:
                count_query += " WHERE merge_session_id = %s"
                cursor.execute(count_query, [merge_session_id])
            else:
                cursor.execute(count_query)
            
            total_count = cursor.fetchone()[0]
            
            return {
                'success': True,
                'data': data,
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