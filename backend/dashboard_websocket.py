import asyncio
import websockets
import json
import logging
from datetime import datetime
from dashboard_api import get_dashboard_metrics, get_db_connection
import pymysql

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store connected clients
connected_clients = set()

async def register(websocket):
    """Register a new client connection"""
    connected_clients.add(websocket)
    logger.info(f"Client connected. Total clients: {len(connected_clients)}")

async def unregister(websocket):
    """Unregister a client connection"""
    connected_clients.remove(websocket)
    logger.info(f"Client disconnected. Total clients: {len(connected_clients)}")

async def send_dashboard_update():
    """Send dashboard metrics to all connected clients"""
    if not connected_clients:
        return
    
    try:
        # Get latest metrics
        metrics = get_dashboard_metrics()
        message = {
            "type": "dashboard_update",
            "timestamp": datetime.now().isoformat(),
            "data": metrics
        }
        
        # Send to all connected clients
        websockets_to_remove = set()
        for websocket in connected_clients:
            try:
                await websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                websockets_to_remove.add(websocket)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                websockets_to_remove.add(websocket)
        
        # Remove disconnected clients
        for websocket in websockets_to_remove:
            await unregister(websocket)
            
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")

async def periodic_update():
    """Send periodic updates every 10 seconds"""
    while True:
        await send_dashboard_update()
        await asyncio.sleep(10)  # Update every 10 seconds

async def websocket_handler(websocket, path):
    """Handle WebSocket connections"""
    await register(websocket)
    try:
        # Send initial data
        metrics = get_dashboard_metrics()
        initial_message = {
            "type": "initial_data",
            "timestamp": datetime.now().isoformat(),
            "data": metrics
        }
        await websocket.send(json.dumps(initial_message))
        
        # Keep connection alive and handle incoming messages
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "ping":
                    await websocket.send(json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}))
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON from client")
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await unregister(websocket)

async def main():
    """Main function to start the WebSocket server"""
    # Start the periodic update task
    update_task = asyncio.create_task(periodic_update())
    
    # Start the WebSocket server with proper handler
    async def handler(websocket):
        await websocket_handler(websocket, None)
    
    server = await websockets.serve(
        handler,
        "localhost",
        8002,
        ping_interval=20,
        ping_timeout=10
    )
    
    logger.info("Dashboard WebSocket server started on ws://localhost:8002")
    
    try:
        await asyncio.gather(server.wait_closed(), update_task)
    except KeyboardInterrupt:
        logger.info("Shutting down WebSocket server...")
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main()) 