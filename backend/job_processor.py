import pymysql
import time
import threading
import logging
import os
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'thanuja',
    'database': 'toolinformation'
}

class JobProcessor:
    def __init__(self):
        self.running = False
        self.processing_thread = None
        self.active_jobs = {}  # Track active job processes
        
    def get_db_connection(self):
        """Create and return a database connection"""
        try:
            connection = pymysql.connect(**DB_CONFIG, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
            return connection
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None
    
    def get_pending_jobs(self):
        """Get all pending jobs from the database"""
        try:
            connection = self.get_db_connection()
            if not connection:
                return []
            
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, user_id, tool_id, state, username, starting_name, created_at
                        FROM jobs 
                        WHERE status = 'pending'
                        ORDER BY created_at ASC
                    """)
                    
                    results = cursor.fetchall()
                    jobs = []
                    for row in results:
                        jobs.append({
                            'id': row['id'],
                            'user_id': row['user_id'],
                            'tool_id': row['tool_id'],
                            'state': row['state'],
                            'username': row['username'],
                            'starting_name': row['starting_name'],
                            'created_at': row['created_at']
                        })
                    
                    return jobs
                    
        except Exception as e:
            logger.error(f"Error getting pending jobs: {e}")
            return []
    
    def update_job_status(self, job_id: str, status: str, progress: int = 0, output_files: Optional[list] = None):
        """Update job status in the database"""
        try:
            connection = self.get_db_connection()
            if not connection:
                return False
            
            with connection:
                with connection.cursor() as cursor:
                    if status == 'running':
                        cursor.execute("""
                            UPDATE jobs 
                            SET status = %s, progress = %s, start_time = NOW()
                            WHERE id = %s
                        """, (status, progress, job_id))
                    elif status in ['completed', 'failed']:
                        cursor.execute("""
                            UPDATE jobs 
                            SET status = %s, progress = %s, end_time = NOW(), output_files = %s
                            WHERE id = %s
                        """, (status, progress, output_files or [], job_id))
                    else:
                        cursor.execute("""
                            UPDATE jobs 
                            SET status = %s, progress = %s
                            WHERE id = %s
                        """, (status, progress, job_id))
                    
                    connection.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
            return False
    
    def process_job(self, job: Dict[str, Any]):
        """Process a single job"""
        job_id = job['id']
        logger.info(f"Starting to process job {job_id}")
        
        try:
            # Update job status to running
            self.update_job_status(job_id, 'running', 0)
            
            # Get tool information
            connection = self.get_db_connection()
            if not connection:
                self.update_job_status(job_id, 'failed', 0)
                return
            
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name, category FROM tools WHERE id = %s", (job['tool_id'],))
                    tool_result = cursor.fetchone()
                    if not tool_result:
                        logger.error(f"Tool not found for job {job_id}")
                        self.update_job_status(job_id, 'failed', 0)
                        return
                    
                    tool_name = tool_result['name']
                    tool_category = tool_result['category']
            
            # Process based on tool category
            if tool_category == 'gem':
                self.process_gem_job(job, tool_name)
            elif tool_category == 'eprocurement':
                self.process_eproc_job(job, tool_name)
            else:
                # Generic processing for other tools
                self.process_generic_job(job, tool_name)
                
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {e}")
            self.update_job_status(job_id, 'failed', 0)
    
    def process_gem_job(self, job: Dict[str, Any], tool_name: str):
        """Process GEM portal scraping job"""
        job_id = job['id']
        
        try:
            # Create output directory
            output_dir = os.path.join('backend', 'outputs', 'gem', str(int(time.time() * 1000)))
            os.makedirs(output_dir, exist_ok=True)
            
            # Update progress
            self.update_job_status(job_id, 'running', 10)
            
            # Run the GEM scraper
            gem_script = os.path.join('backend', 'scrapers', 'gem.py')
            if os.path.exists(gem_script):
                cmd = [
                    'python', gem_script,
                    '--startingpage', '1',
                    '--totalpages', '1',
                    '--username', job['username'],
                    '--state_index', '0',
                    '--days_interval', '1',
                    '--run_id', job_id
                ]
                
                # Update progress
                self.update_job_status(job_id, 'running', 30)
                
                # Run the process
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True,
                    cwd=os.path.join('backend', 'scrapers')
                )
                
                # Store the process
                self.active_jobs[job_id] = process
                
                # Monitor the process
                output_files = []
                for line in iter(process.stdout.readline, ''):
                    if line.startswith("File written:"):
                        file_path = line.split("File written:", 1)[1].strip()
                        output_files.append(os.path.basename(file_path))
                
                process.wait()
                
                # Remove from active jobs
                if job_id in self.active_jobs:
                    del self.active_jobs[job_id]
                
                # Check if process was successful
                if process.returncode == 0:
                    self.update_job_status(job_id, 'completed', 100, output_files)
                    logger.info(f"Job {job_id} completed successfully")
                else:
                    self.update_job_status(job_id, 'failed', 0)
                    logger.error(f"Job {job_id} failed with return code {process.returncode}")
            else:
                logger.error(f"GEM script not found: {gem_script}")
                self.update_job_status(job_id, 'failed', 0)
                
        except Exception as e:
            logger.error(f"Error in GEM job processing: {e}")
            self.update_job_status(job_id, 'failed', 0)
    
    def process_eproc_job(self, job: Dict[str, Any], tool_name: str):
        """Process E-Procurement scraping job"""
        job_id = job['id']
        
        try:
            # Update progress
            self.update_job_status(job_id, 'running', 20)
            
            # For now, simulate E-Procurement processing
            # In a real implementation, this would call the appropriate scraper
            time.sleep(2)  # Simulate processing time
            
            # Update progress
            self.update_job_status(job_id, 'running', 60)
            
            # Simulate completion
            time.sleep(1)
            self.update_job_status(job_id, 'completed', 100, ['eproc_output.xlsx'])
            
        except Exception as e:
            logger.error(f"Error in E-Procurement job processing: {e}")
            self.update_job_status(job_id, 'failed', 0)
    
    def process_generic_job(self, job: Dict[str, Any], tool_name: str):
        """Process generic job"""
        job_id = job['id']
        
        try:
            # Simulate generic processing
            for progress in [20, 40, 60, 80, 100]:
                self.update_job_status(job_id, 'running', progress)
                time.sleep(1)
            
            self.update_job_status(job_id, 'completed', 100, [f'{tool_name}_output.xlsx'])
            
        except Exception as e:
            logger.error(f"Error in generic job processing: {e}")
            self.update_job_status(job_id, 'failed', 0)
    
    def stop_job(self, job_id: str):
        """Stop a running job"""
        if job_id in self.active_jobs:
            process = self.active_jobs[job_id]
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping job {job_id}: {e}")
            finally:
                del self.active_jobs[job_id]
                self.update_job_status(job_id, 'stopped', 0)
    
    def process_jobs_loop(self):
        """Main loop for processing jobs"""
        while self.running:
            try:
                # Get pending jobs
                pending_jobs = self.get_pending_jobs()
                
                # Process each pending job
                for job in pending_jobs:
                    if not self.running:
                        break
                    
                    # Check if we should process this job
                    if job['id'] not in self.active_jobs:
                        self.process_job(job)
                
                # Sleep before next iteration
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in job processing loop: {e}")
                time.sleep(10)  # Wait longer on error
    
    def start(self):
        """Start the job processor"""
        if not self.running:
            self.running = True
            self.processing_thread = threading.Thread(target=self.process_jobs_loop, daemon=True)
            self.processing_thread.start()
            logger.info("Job processor started")
    
    def stop(self):
        """Stop the job processor"""
        self.running = False
        
        # Stop all active jobs
        for job_id in list(self.active_jobs.keys()):
            self.stop_job(job_id)
        
        # Wait for processing thread to finish
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=10)
        
        logger.info("Job processor stopped")

# Global job processor instance
job_processor = JobProcessor()

def start_job_processor():
    """Start the global job processor"""
    job_processor.start()

def stop_job_processor():
    """Stop the global job processor"""
    job_processor.stop()

if __name__ == "__main__":
    # Start the job processor
    start_job_processor()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping job processor...")
        stop_job_processor() 