#!/bin/bash
cd frontend
export BROWSER=none
export PORT=3000  
export REACT_APP_API_URL=http://localhost:8000
npm start
