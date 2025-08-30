#!/usr/bin/env python3
import sqlite3
import time
import json
import sys
from pathlib import Path

def test_database_performance(db_path, results_file):
    """Test database performance with realistic queries"""
    
    results = {
        "timestamp": time.time(),
        "database_path": str(db_path),
        "tests": {}
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Simple SELECT query
        start_time = time.perf_counter()
        cursor.execute("SELECT COUNT(*) FROM horses")
        result = cursor.fetchone()
        query_time = (time.perf_counter() - start_time) * 1000
        
        results["tests"]["simple_count"] = {
            "query": "SELECT COUNT(*) FROM horses",
            "time_ms": round(query_time, 2),
            "result_count": result[0] if result else 0,
            "status": "pass" if query_time < 100 else "warning"
        }
        
        # Test 2: Complex JOIN query
        start_time = time.perf_counter()
        cursor.execute("""
            SELECT h.horse_name, j.jockey_name, t.trainer_name, r.position
            FROM horses h
            JOIN results_horses rh ON h.horse_id = rh.horse_id
            JOIN jockeys_stats j ON rh.jockey_id = j.jockey_id
            JOIN trainers_stats t ON h.trainer_id = t.trainer_id
            JOIN records r ON rh.race_id = r.race_id
            LIMIT 100
        """)
        results_data = cursor.fetchall()
        query_time = (time.perf_counter() - start_time) * 1000
        
        results["tests"]["complex_join"] = {
            "query": "Complex JOIN with 4 tables",
            "time_ms": round(query_time, 2),
            "result_count": len(results_data),
            "status": "pass" if query_time < 500 else "warning"
        }
        
        # Test 3: Aggregation query
        start_time = time.perf_counter()
        cursor.execute("""
            SELECT trainer_name, COUNT(*) as horse_count, AVG(win_rate) as avg_win_rate
            FROM trainers_stats
            GROUP BY trainer_name
            ORDER BY avg_win_rate DESC
            LIMIT 20
        """)
        agg_results = cursor.fetchall()
        query_time = (time.perf_counter() - start_time) * 1000
        
        results["tests"]["aggregation"] = {
            "query": "GROUP BY with aggregations",
            "time_ms": round(query_time, 2),
            "result_count": len(agg_results),
            "status": "pass" if query_time < 200 else "warning"
        }
        
        # Test 4: Full text search simulation
        start_time = time.perf_counter()
        cursor.execute("""
            SELECT * FROM horses 
            WHERE horse_name LIKE '%STAR%' 
            OR horse_name LIKE '%GOLD%'
            LIMIT 50
        """)
        search_results = cursor.fetchall()
        query_time = (time.perf_counter() - start_time) * 1000
        
        results["tests"]["text_search"] = {
            "query": "LIKE pattern matching",
            "time_ms": round(query_time, 2),
            "result_count": len(search_results),
            "status": "pass" if query_time < 150 else "warning"
        }
        
        conn.close()
        
        # Calculate summary
        total_time = sum(test["time_ms"] for test in results["tests"].values())
        passed_tests = len([test for test in results["tests"].values() if test["status"] == "pass"])
        total_tests = len(results["tests"])
        
        results["summary"] = {
            "total_time_ms": round(total_time, 2),
            "average_time_ms": round(total_time / total_tests, 2),
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "success_rate": round((passed_tests / total_tests) * 100, 2)
        }
        
    except Exception as e:
        results["error"] = str(e)
        results["status"] = "failed"
    
    # Save results
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "racing_data.db"
    results_file = sys.argv[2] if len(sys.argv) > 2 else "db_performance.json"
    
    results = test_database_performance(db_path, results_file)
    
    print(f"Database Performance Test Results:")
    print(f"Total Time: {results.get('summary', {}).get('total_time_ms', 0)}ms")
    print(f"Success Rate: {results.get('summary', {}).get('success_rate', 0)}%")
    
    if results.get('summary', {}).get('success_rate', 0) >= 80:
        sys.exit(0)
    else:
        sys.exit(1)
