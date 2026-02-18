from quart import Quart, render_template_string
import os

app = Quart(__name__)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Zemi Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #1a1a1a;
            color: #fff;
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        h1 {
            color: #4CAF50;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        .status-card {
            background: #2a2a2a;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #4CAF50;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
        }
        .status-label {
            color: #999;
        }
        .status-value {
            color: #4CAF50;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Zemi V1 Dashboard</h1>
        
        <div class="status-card">
            <h2>System Status</h2>
            <div class="status-item">
                <span class="status-label">Ollama:</span>
                <span class="status-value">✓ Running</span>
            </div>
            <div class="status-item">
                <span class="status-label">Matrix:</span>
                <span class="status-value">✓ Running</span>
            </div>
            <div class="status-item">
                <span class="status-label">Browser:</span>
                <span class="status-value">✓ Running</span>
            </div>
            <div class="status-item">
                <span class="status-label">Tailscale:</span>
                <span class="status-value">✓ Connected</span>
            </div>
        </div>
        
        <div class="status-card">
            <h2>Access Info</h2>
            <div class="status-item">
                <span class="status-label">Tailscale IP:</span>
                <span class="status-value">100.111.133.70</span>
            </div>
            <div class="status-item">
                <span class="status-label">Matrix:</span>
                <span class="status-value">http://100.111.133.70:8008</span>
            </div>
        </div>
        
        <div class="status-card">
            <h2>Quick Stats</h2>
            <div class="status-item">
                <span class="status-label">Uptime:</span>
                <span class="status-value">Running</span>
            </div>
            <div class="status-item">
                <span class="status-label">Security:</span>
                <span class="status-value">✓ Encrypted</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
async def index():
    return await render_template_string(DASHBOARD_HTML)

if __name__ == '__main__':
    app.run()
