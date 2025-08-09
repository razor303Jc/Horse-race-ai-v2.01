#!/usr/bin/env python3
"""
Flask Web App Integration Example
================================
Example Flask routes for integrating racing analysis with web app.
"""

import json
import os
from datetime import date, datetime
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request

from webapp_racing_interface import WebAppRacingInterface

app = Flask(__name__)

# Initialize racing interface
racing_interface = WebAppRacingInterface("reports")


@app.route("/api/racing/analyze", methods=["POST"])
def request_racing_analysis():
    """API endpoint to request new racing analysis."""
    try:
        data = request.get_json() or {}
        target_date = data.get("date", "today")

        # Start background analysis
        result = racing_interface.request_analysis(target_date, "json")

        if "error" in result:
            return jsonify({"success": False, "error": result["error"]}), 400

        return jsonify(
            {"success": True, "message": "Analysis completed", "data": result}
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/racing/report/<date_str>")
def get_racing_report(date_str):
    """API endpoint to get racing report for a specific date."""
    try:
        result = racing_interface._get_latest_report(date_str, "json")

        if "error" in result:
            return jsonify({"success": False, "error": result["error"]}), 404

        return jsonify({"success": True, "data": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/racing/reports")
def list_racing_reports():
    """API endpoint to list all available reports."""
    try:
        result = racing_interface.get_available_reports()
        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/racing/report/<date_str>")
def view_racing_report(date_str):
    """Web page to view racing report."""
    try:
        result = racing_interface._get_latest_report(date_str, "html")

        if "error" in result:
            return f"<h1>Error</h1><p>{result['error']}</p>", 404

        return result["html_content"]

    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>", 500


@app.route("/racing/dashboard")
def racing_dashboard():
    """Racing analysis dashboard."""
    template = """
<!DOCTYPE html>
<html>
<head>
    <title>Racing Analysis Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        .reports-list { margin-top: 20px; }
        .report-item { padding: 10px; border-bottom: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏇 Racing Analysis Dashboard</h1>
        
        <div class="card">
            <h3>Request New Analysis</h3>
            <form id="analysisForm">
                <label>Date:</label>
                <select id="dateSelect">
                    <option value="today">Today</option>
                    <option value="tomorrow">Tomorrow</option>
                    <option value="yesterday">Yesterday</option>
                </select>
                <button type="submit" class="btn">Start Analysis</button>
            </form>
            <div id="analysisStatus"></div>
        </div>
        
        <div class="card">
            <h3>Available Reports</h3>
            <div id="reportsList" class="reports-list">
                Loading reports...
            </div>
        </div>
    </div>

    <script>
        // Load available reports
        function loadReports() {
            fetch('/api/racing/reports')
                .then(response => response.json())
                .then(data => {
                    const reportsDiv = document.getElementById('reportsList');
                    if (data.reports && data.reports.length > 0) {
                        reportsDiv.innerHTML = data.reports.map(report => 
                            `<div class="report-item">
                                <strong>${report.date}</strong> - ${report.time}
                                <a href="/racing/report/${report.date}" target="_blank">View Report</a>
                            </div>`
                        ).join('');
                    } else {
                        reportsDiv.innerHTML = 'No reports available';
                    }
                })
                .catch(error => {
                    document.getElementById('reportsList').innerHTML = 'Error loading reports';
                });
        }
        
        // Handle analysis request
        document.getElementById('analysisForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const date = document.getElementById('dateSelect').value;
            const statusDiv = document.getElementById('analysisStatus');
            
            statusDiv.innerHTML = '🔄 Starting analysis...';
            
            fetch('/api/racing/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ date: date })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    statusDiv.innerHTML = '✅ Analysis completed!';
                    loadReports(); // Reload reports list
                } else {
                    statusDiv.innerHTML = `❌ Error: ${data.error}`;
                }
            })
            .catch(error => {
                statusDiv.innerHTML = `❌ Error: ${error.message}`;
            });
        });
        
        // Load reports on page load
        loadReports();
    </script>
</body>
</html>
    """
    return render_template_string(template)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
