#!/usr/bin/env python3
"""
PostgreSQL Performance Benchmark for Horse Racing v2.05
Test comprehensive database performance under realistic workloads
"""
import psycopg2
import time
import statistics
from datetime import datetime

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "results",
    "user": "horse_racing",
    "password": "horse_racing_password",
}


def connect_db():
    """Establish database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None


def benchmark_query(conn, query_name, query, iterations=5):
    """Benchmark a query with multiple iterations"""
    print(f"\n📊 Benchmarking: {query_name}")
    print(f"Query: {query}")

    times = []
    cursor = conn.cursor()

    for i in range(iterations):
        start_time = time.time()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            end_time = time.time()

            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
            times.append(execution_time)

            print(f"  Iteration {i+1}: {execution_time:.2f}ms ({len(result)} rows)")

        except Exception as e:
            print(f"  Iteration {i+1}: ERROR - {e}")
            return None

    cursor.close()

    # Calculate statistics
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    median_time = statistics.median(times)

    print(f"  📈 Results:")
    print(f"    Average: {avg_time:.2f}ms")
    print(f"    Median:  {median_time:.2f}ms")
    print(f"    Min:     {min_time:.2f}ms")
    print(f"    Max:     {max_time:.2f}ms")

    # Performance assessment
    if avg_time < 10:
        status = "🟢 EXCELLENT"
    elif avg_time < 50:
        status = "🟡 GOOD"
    elif avg_time < 100:
        status = "🟠 ACCEPTABLE"
    else:
        status = "🔴 NEEDS OPTIMIZATION"

    print(f"    Status:  {status}")

    return {
        "query_name": query_name,
        "avg_time": avg_time,
        "median_time": median_time,
        "min_time": min_time,
        "max_time": max_time,
        "status": status,
    }


def run_comprehensive_benchmark():
    """Run comprehensive PostgreSQL performance benchmark"""
    print("🚀 PostgreSQL Performance Benchmark for Horse Racing v2.05")
    print("=" * 60)

    conn = connect_db()
    if not conn:
        print("❌ Failed to connect to database")
        return

    print(f"✅ Connected to PostgreSQL at {datetime.now()}")

    # Define benchmark queries
    benchmark_queries = [
        ("Entity Count Check", "SELECT COUNT(*) FROM horses_entity;"),
        ("Jockey Count Check", "SELECT COUNT(*) FROM jockeys_entity;"),
        ("Trainer Count Check", "SELECT COUNT(*) FROM trainers_entity;"),
        ("Racing Data Count", "SELECT COUNT(*) FROM races;"),
        (
            "Racing Date Query",
            "SELECT date, course, COUNT(*) FROM races GROUP BY date, course ORDER BY date, course;",
        ),
        (
            "Complex Racing Query",
            """
            SELECT 
                r.course, 
                r.race_type,
                COUNT(*) as races,
                AVG(r.runners) as avg_runners,
                SUM(r.runners) as total_runners
            FROM races r 
            WHERE r.date = '2025-08-25'
            GROUP BY r.course, r.race_type 
            ORDER BY total_runners DESC;
        """,
        ),
        (
            "Horse Age Distribution",
            "SELECT age, COUNT(*) FROM horses_entity GROUP BY age ORDER BY age;",
        ),
        (
            "Jockey Performance Stats",
            """
            SELECT 
                LEFT(jockey_name, 1) as first_letter,
                COUNT(*) as jockey_count
            FROM jockeys_entity 
            GROUP BY LEFT(jockey_name, 1) 
            ORDER BY jockey_count DESC 
            LIMIT 10;
        """,
        ),
        (
            "Racing Surface Analysis",
            """
            SELECT 
                CASE 
                    WHEN race_type LIKE '%Flat%' THEN 'Flat'
                    WHEN race_type LIKE '%Hurdle%' THEN 'Hurdle'
                    WHEN race_type LIKE '%Chase%' THEN 'Chase'
                    ELSE 'Other'
                END as surface_type,
                COUNT(*) as race_count,
                AVG(runners) as avg_field_size
            FROM races
            GROUP BY surface_type
            ORDER BY race_count DESC;
        """,
        ),
        (
            "Index Performance Test",
            "SELECT * FROM races WHERE date = '2025-08-25' AND course = 'Ripon' ORDER BY race_number;",
        ),
    ]

    results = []

    # Run all benchmarks
    for query_name, query in benchmark_queries:
        result = benchmark_query(conn, query_name, query)
        if result:
            results.append(result)

    # Summary report
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE BENCHMARK SUMMARY")
    print("=" * 60)

    total_queries = len(results)
    excellent_count = sum(1 for r in results if "EXCELLENT" in r["status"])
    good_count = sum(1 for r in results if "GOOD" in r["status"])
    acceptable_count = sum(1 for r in results if "ACCEPTABLE" in r["status"])
    needs_optimization = sum(1 for r in results if "NEEDS OPTIMIZATION" in r["status"])

    print(f"Total Queries Tested: {total_queries}")
    print(f"🟢 Excellent (<10ms): {excellent_count}")
    print(f"🟡 Good (10-50ms): {good_count}")
    print(f"🟠 Acceptable (50-100ms): {acceptable_count}")
    print(f"🔴 Needs Optimization (>100ms): {needs_optimization}")

    if results:
        avg_times = [r["avg_time"] for r in results]
        overall_avg = statistics.mean(avg_times)
        overall_median = statistics.median(avg_times)

        print(f"\nOverall Performance:")
        print(f"  Average Response Time: {overall_avg:.2f}ms")
        print(f"  Median Response Time: {overall_median:.2f}ms")

        if overall_avg < 50:
            print(f"  🎉 OVERALL STATUS: EXCELLENT - Ready for production!")
        elif overall_avg < 100:
            print(f"  ✅ OVERALL STATUS: GOOD - Suitable for testing and simulation")
        else:
            print(f"  ⚠️  OVERALL STATUS: Needs optimization before heavy usage")

    # Detailed results table
    print(f"\nDetailed Results:")
    print(f"{'Query':<25} {'Avg Time':<10} {'Status':<20}")
    print("-" * 55)
    for result in results:
        print(
            f"{result['query_name']:<25} {result['avg_time']:<9.2f}ms {result['status']:<20}"
        )

    conn.close()
    print(f"\n✅ Benchmark completed at {datetime.now()}")
    print("🚀 PostgreSQL ready for Testing & Simulation Strategy!")


if __name__ == "__main__":
    run_comprehensive_benchmark()
