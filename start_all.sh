#!/bin/bash
# Start backend server
poetry run python mcp-server-elasticsearch/chat/server.py &
SERVER_PID=$!
# Wait a few seconds for the server to start
sleep 3
# Start Chainlit app
poetry run chainlit run chatbot/chainlit_app.py --port 8001 --watch
# When Chainlit exits, stop the server
kill $SERVER_PID
