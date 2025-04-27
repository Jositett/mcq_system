import unittest
import asyncio
from unittest.mock import Mock, patch
from src.utils.network_state import NetworkState
import httpx

class TestNetworkState(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.network_state = NetworkState()
        self.callback_called = False
        self.callback_value = None
    
    async def asyncTearDown(self):
        # Ensure monitoring is stopped and task is cancelled
        self.network_state.stop_monitoring()
        if self.network_state._check_task:
            try:
                await self.network_state._check_task
            except asyncio.CancelledError:
                pass
        await asyncio.sleep(0.1)  # Let cancellation take effect
    
    def network_callback(self, is_online: bool):
        self.callback_called = True
        self.callback_value = is_online
    
    async def test_initial_state(self):
        self.assertTrue(self.network_state.is_online)
        self.assertEqual(len(self.network_state._listeners), 0)
    
    def test_add_remove_listener(self):
        # Add listener
        self.network_state.add_listener(self.network_callback)
        self.assertEqual(len(self.network_state._listeners), 1)
        
        # Add same listener again (should not duplicate)
        self.network_state.add_listener(self.network_callback)
        self.assertEqual(len(self.network_state._listeners), 1)
        
        # Remove listener
        self.network_state.remove_listener(self.network_callback)
        self.assertEqual(len(self.network_state._listeners), 0)
    
    async def test_check_connection_success(self):
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value.status_code = 200
            
            self.network_state.add_listener(self.network_callback)
            is_online = await self.network_state.check_connection("http://test-api")
            
            self.assertTrue(is_online)
            self.assertTrue(self.network_state.is_online)
            self.assertFalse(self.callback_called)  # No state change, no callback
    
    async def test_check_connection_failure(self):
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")
            
            self.network_state.add_listener(self.network_callback)
            is_online = await self.network_state.check_connection("http://test-api")
            
            self.assertFalse(is_online)
            self.assertFalse(self.network_state.is_online)
            self.assertTrue(self.callback_called)
            self.assertFalse(self.callback_value)
    
    async def test_state_change_notification(self):
        self.network_state.add_listener(self.network_callback)
        
        # Test transition to offline
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")
            await self.network_state.check_connection("http://test-api")
            
            self.assertTrue(self.callback_called)
            self.assertFalse(self.callback_value)
        
        # Reset callback flags
        self.callback_called = False
        self.callback_value = None
        
        # Test transition back to online
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value.status_code = 200
            await self.network_state.check_connection("http://test-api")
            
            self.assertTrue(self.callback_called)
            self.assertTrue(self.callback_value)
    
    async def test_monitoring_loop(self):
        # Start monitoring with a short interval
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value.status_code = 200
            await self.network_state.start_monitoring("http://test-api", interval=0.1)
            
            # Wait for the task to start
            for _ in range(10):
                if self.network_state._check_task:
                    break
                await asyncio.sleep(0.1)
                
            self.assertIsNotNone(self.network_state._check_task)
            self.assertFalse(self.network_state._check_task.done())
            
            # Let it run for a short time
            await asyncio.sleep(0.3)
            
            # Stop monitoring
            self.network_state.stop_monitoring()
            
            # Wait for task to actually stop
            for _ in range(5):
                if self.network_state._check_task.cancelled():
                    break
                await asyncio.sleep(0.1)
            
            # Verify task was cancelled
            self.assertTrue(self.network_state._check_task.cancelled())
            
            # Verify multiple checks occurred
            self.assertGreater(mock_get.call_count, 1)

if __name__ == "__main__":
    unittest.main()