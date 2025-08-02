// Test script to verify frontend-backend connection
const API_BASE_URL = 'http://localhost:8000';

async function testConnection() {
    console.log('🧪 Testing Frontend-Backend Connection...');
    
    try {
        // Test analytics health endpoint
        const healthResponse = await fetch(`${API_BASE_URL}/analytics/health`);
        console.log('✅ Health endpoint:', healthResponse.status);
        
        if (healthResponse.ok) {
            const healthData = await healthResponse.json();
            console.log('   Response:', healthData);
        }
        
        // Test performance endpoint
        const performanceResponse = await fetch(`${API_BASE_URL}/analytics/performance`);
        console.log('✅ Performance endpoint:', performanceResponse.status);
        
        if (performanceResponse.ok) {
            const performanceData = await performanceResponse.json();
            console.log('   Total Jobs:', performanceData.metrics?.totalJobs?.value);
            console.log('   Success Rate:', performanceData.metrics?.successRate?.value);
        } else {
            console.log('   Error:', await performanceResponse.text());
        }
        
        // Test recent jobs endpoint
        const recentJobsResponse = await fetch(`${API_BASE_URL}/analytics/recent-jobs`);
        console.log('✅ Recent jobs endpoint:', recentJobsResponse.status);
        
        if (recentJobsResponse.ok) {
            const recentJobsData = await recentJobsResponse.json();
            console.log('   Recent jobs count:', recentJobsData.recentJobs?.length);
        } else {
            console.log('   Error:', await recentJobsResponse.text());
        }
        
    } catch (error) {
        console.error('❌ Connection failed:', error.message);
        console.log('💡 Make sure:');
        console.log('   1. Backend is running on port 8000');
        console.log('   2. No firewall blocking the connection');
        console.log('   3. CORS is properly configured');
    }
}

// Run the test
testConnection(); 