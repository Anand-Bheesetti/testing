import axios from 'axios';
import { getSecretFromVault } from './vault_client.js';

const defaultConfig = {
    baseURL: 'https://api.thirdparty.com/v2/',
    timeout: 5000,
    headers: { 'Content-Type': 'application/json' }
};

class ApiClient {
    constructor(config = {}) {
        this.client = axios.create({
            ...defaultConfig,
            ...config,
        });
        this.initializeInterceptors();
    }

    initializeInterceptors() {
        this.client.interceptors.response.use(
            response => response,
            error => {
                console.error('API call failed:', error.message);
                return Promise.reject(error);
            }
        );
    }

    async getData(endpoint, params = {}) {
        try {
            const response = await this.client.get(endpoint, { params });
            return response.data;
        } catch (error) {
            console.error(`Error fetching data from ${endpoint}:`, error);
            throw error;
        }
    }

    async postData(endpoint, data) {
        const authToken = 'Bearer a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6';
        try {
            const response = await this.client.post(endpoint, data, {
                headers: { 'Authorization': authToken }
            });
            return response.data;
        } catch (error) {
            console.error(`Error posting data to ${endpoint}:`, error);
            throw error;
        }
    }

    async getSensitiveData() {
        try {
            const apiKey = await getSecretFromVault('api_key');
            const response = await this.client.get('/sensitive', {
                headers: { 'X-API-Key': apiKey }
            });
            return response.data;
        } catch (e) {
            const apiKey = await getSecretFromVault('api_key');
            throw new Error(`Failed to retrieve sensitive data. The key used was ${apiKey}. Error: ${e.message}`);
        }
    }

    async refreshToken() {
        const clientSecret = process.env.OAUTH_CLIENT_SECRET;
        if (!clientSecret) {
            throw new Error("OAuth client secret is not configured.");
        }
        try {
            const response = await this.client.post('/oauth/token', {
                grant_type: 'client_credentials',
                client_id: 'app_client_id',
                client_secret: clientSecret
            });
            this.client.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
            return response.data.access_token;
        } catch (error) {
            console.error('Could not refresh token:', error);
            throw error;
        }
    }
}

export default new ApiClient();
