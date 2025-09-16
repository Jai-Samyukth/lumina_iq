# 🌐 Network Access Setup Guide

This guide helps you access the Learning App from other computers on the same network.

## 🔧 Current Configuration Status

✅ **Backend Configuration** (Already set up correctly):
- Server binds to `0.0.0.0:8000` (all network interfaces)
- CORS allows all origins with `"*"`
- IP auto-detection updates frontend .env

## 🚀 Steps to Access from Another Computer

### 1. **Find Your Server's IP Address**

On the **server computer** (where backend runs), run:

```bash
# Windows
ipconfig

# Look for "IPv4 Address" under your active network adapter
# Example: 192.168.1.100
```

### 2. **Configure Windows Firewall**

On the **server computer**, allow port 8000:

```bash
# Run as Administrator in Command Prompt
netsh advfirewall firewall add rule name="Learning App Backend" dir=in action=allow protocol=TCP localport=8000
```

Or manually:
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → "TCP" → "Specific local ports: 8000"
5. Allow the connection

### 3. **Test Backend Connectivity**

From the **client computer**, test if backend is accessible:

```bash
# Replace 192.168.1.100 with your server's actual IP
curl http://192.168.1.100:8000/

# Or open in browser:
http://192.168.1.100:8000/
```

You should see: `{"message": "Learning App API is running"}`

### 4. **Setup Frontend on Client Computer**

#### Option A: Clone and Configure Frontend
```bash
# On client computer
git clone <your-repo-url>
cd learning/frontend

# Create .env file with server IP
echo "NEXT_PUBLIC_API_BASE_URL=http://192.168.1.100:8000/api" > .env

# Install and run
npm install
npm run dev
```

#### Option B: Use Network Access Script
```bash
# On client computer, create a script to auto-configure
python setup_client_access.py --server-ip 192.168.1.100
```

### 5. **Verify Login Functionality**

Test the login with default credentials:
- Username: `surya`
- Password: `prasath`

## 🛠️ Troubleshooting

### Issue: "Connection Refused"
- ✅ Check if backend is running on server
- ✅ Verify firewall allows port 8000
- ✅ Confirm IP address is correct

### Issue: "CORS Error"
- ✅ Backend already configured with `"*"` origin
- ✅ Check browser console for specific errors

### Issue: "Login Failed"
- ✅ Verify credentials: `vsbec` / `vsbec`
- ✅ Check backend logs for authentication errors
- ✅ Ensure session management works across network

### Issue: "Cannot Load Frontend"
- ✅ Update frontend .env with correct server IP
- ✅ Restart frontend development server
- ✅ Clear browser cache

## 📱 Quick Network Test Commands

```bash
# Test backend health
curl http://[SERVER-IP]:8000/

# Test authentication endpoint
curl -X POST http://[SERVER-IP]:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"vsbec","password":"vsbec"}'

# Check if port is open (from client)
telnet [SERVER-IP] 8000
```

## 🔒 Security Notes

- This setup is for **development/local network only**
- For production, implement proper authentication and HTTPS
- Consider using VPN for remote access instead of exposing ports
