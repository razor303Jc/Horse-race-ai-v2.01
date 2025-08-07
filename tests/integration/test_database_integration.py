"""
Integration tests for database connectivity in containerized environment.

Tests database connectivity including:
- PostgreSQL connection
- Redis connection
- Basic CRUD operations
- Connection pooling
- Transaction handling
"""

import asyncio
import os
import time
from typing import Optional

import asyncpg
import pytest
import redis
import redis.asyncio as aioredis


class TestPostgreSQLIntegration:
    """Integration tests for PostgreSQL database."""

    @pytest.fixture
    def postgres_config(self) -> dict:
        """Get PostgreSQL configuration from environment."""
        return {
            "host": os.getenv("POSTGRES_HOST", "postgres-test"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "horse_racing_test"),
            "user": os.getenv("POSTGRES_USER", "testuser"),
            "password": os.getenv("POSTGRES_PASSWORD", "testpass"),
        }

    @pytest.mark.asyncio
    async def test_postgres_connection(self, postgres_config: dict):
        """Test basic PostgreSQL connection."""
        try:
            conn = await asyncpg.connect(**postgres_config)

            # Test basic query
            result = await conn.fetchval("SELECT 1")
            assert result == 1, "Basic SELECT query should work"

            await conn.close()

        except Exception as e:
            pytest.fail(f"Failed to connect to PostgreSQL: {e}")

    @pytest.mark.asyncio
    async def test_postgres_create_table(self, postgres_config: dict):
        """Test table creation and basic operations."""
        conn = None
        try:
            conn = await asyncpg.connect(**postgres_config)

            # Create test table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS test_races (
                    id SERIAL PRIMARY KEY,
                    race_name VARCHAR(255) NOT NULL,
                    track VARCHAR(100) NOT NULL,
                    race_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Insert test data
            race_id = await conn.fetchval(
                """
                INSERT INTO test_races (race_name, track, race_time)
                VALUES ($1, $2, $3)
                RETURNING id
            """,
                "Test Race",
                "Test Track",
                None,
            )

            assert race_id is not None, "Insert should return an ID"

            # Query the data back
            race = await conn.fetchrow(
                """
                SELECT race_name, track FROM test_races WHERE id = $1
            """,
                race_id,
            )

            assert race["race_name"] == "Test Race"
            assert race["track"] == "Test Track"

            # Clean up
            await conn.execute("DELETE FROM test_races WHERE id = $1", race_id)

        except Exception as e:
            pytest.fail(f"Database operations failed: {e}")
        finally:
            if conn:
                await conn.close()

    @pytest.mark.asyncio
    async def test_postgres_transaction(self, postgres_config: dict):
        """Test transaction handling."""
        conn = None
        try:
            conn = await asyncpg.connect(**postgres_config)

            # Create test table if it doesn't exist
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS test_transactions (
                    id SERIAL PRIMARY KEY,
                    value INTEGER NOT NULL
                )
            """
            )

            # Test successful transaction
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO test_transactions (value) VALUES ($1)", 42
                )
                await conn.execute(
                    "INSERT INTO test_transactions (value) VALUES ($1)", 24
                )

            # Verify data was committed
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM test_transactions WHERE value IN (42, 24)"
            )
            assert count == 2, "Transaction should have committed both inserts"

            # Test transaction rollback
            try:
                async with conn.transaction():
                    await conn.execute(
                        "INSERT INTO test_transactions (value) VALUES ($1)", 99
                    )
                    # Force an error to trigger rollback
                    await conn.execute("SELECT 1/0")
            except Exception:
                pass  # Expected

            # Verify rollback worked
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM test_transactions WHERE value = 99"
            )
            assert count == 0, "Transaction should have been rolled back"

            # Clean up
            await conn.execute("DELETE FROM test_transactions WHERE value IN (42, 24)")

        except Exception as e:
            pytest.fail(f"Transaction test failed: {e}")
        finally:
            if conn:
                await conn.close()

    @pytest.mark.asyncio
    async def test_postgres_connection_pool(self, postgres_config: dict):
        """Test connection pooling."""
        pool = None
        try:
            pool = await asyncpg.create_pool(**postgres_config, min_size=2, max_size=5)

            # Test multiple concurrent connections
            async def test_query(query_id: int):
                async with pool.acquire() as conn:
                    result = await conn.fetchval("SELECT $1", query_id)
                    return result

            # Run 5 concurrent queries
            tasks = [test_query(i) for i in range(5)]
            results = await asyncio.gather(*tasks)

            assert results == list(range(5)), "All queries should succeed"

        except Exception as e:
            pytest.fail(f"Connection pool test failed: {e}")
        finally:
            if pool:
                await pool.close()


class TestRedisIntegration:
    """Integration tests for Redis."""

    @pytest.fixture
    def redis_config(self) -> dict:
        """Get Redis configuration from environment."""
        return {
            "host": os.getenv("REDIS_HOST", "redis-test"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "db": int(os.getenv("REDIS_DB", "0")),
            "decode_responses": True,
        }

    def test_redis_sync_connection(self, redis_config: dict):
        """Test synchronous Redis connection."""
        try:
            client = redis.Redis(**redis_config)

            # Test basic ping
            response = client.ping()
            assert response is True, "Redis ping should succeed"

            # Test basic set/get
            test_key = "test:integration"
            test_value = "integration_test_value"

            client.set(test_key, test_value, ex=60)  # 60 second expiry
            retrieved = client.get(test_key)

            assert retrieved == test_value, "Set/get should work correctly"

            # Clean up
            client.delete(test_key)

            client.close()

        except Exception as e:
            pytest.fail(f"Failed to connect to Redis: {e}")

    @pytest.mark.asyncio
    async def test_redis_async_connection(self, redis_config: dict):
        """Test asynchronous Redis connection."""
        client = None
        try:
            client = aioredis.Redis(**redis_config)

            # Test async ping
            response = await client.ping()
            assert response is True, "Async Redis ping should succeed"

            # Test async set/get
            test_key = "test:async:integration"
            test_value = "async_integration_test"

            await client.set(test_key, test_value, ex=60)
            retrieved = await client.get(test_key)

            assert retrieved == test_value, "Async set/get should work"

            # Clean up
            await client.delete(test_key)

        except Exception as e:
            pytest.fail(f"Async Redis connection failed: {e}")
        finally:
            if client:
                await client.aclose()

    @pytest.mark.asyncio
    async def test_redis_data_structures(self, redis_config: dict):
        """Test Redis data structures (lists, sets, hashes)."""
        client = None
        try:
            client = aioredis.Redis(**redis_config)

            # Test list operations
            list_key = "test:list"
            await client.delete(list_key)  # Clean start

            await client.lpush(list_key, "item1", "item2", "item3")
            length = await client.llen(list_key)
            assert length == 3, "List should have 3 items"

            items = await client.lrange(list_key, 0, -1)
            assert "item1" in items, "List should contain pushed items"

            # Test hash operations
            hash_key = "test:hash"
            await client.delete(hash_key)

            await client.hset(
                hash_key,
                mapping={
                    "horse_name": "Test Horse",
                    "odds": "3.5",
                    "track": "Test Track",
                },
            )

            horse_name = await client.hget(hash_key, "horse_name")
            assert horse_name == "Test Horse", "Hash field should be retrievable"

            all_hash = await client.hgetall(hash_key)
            assert len(all_hash) == 3, "Hash should have 3 fields"

            # Test set operations
            set_key = "test:set"
            await client.delete(set_key)

            await client.sadd(set_key, "member1", "member2", "member3")
            members = await client.smembers(set_key)
            assert len(members) == 3, "Set should have 3 members"

            # Clean up
            await client.delete(list_key, hash_key, set_key)

        except Exception as e:
            pytest.fail(f"Redis data structures test failed: {e}")
        finally:
            if client:
                await client.aclose()

    @pytest.mark.asyncio
    async def test_redis_pubsub(self, redis_config: dict):
        """Test Redis pub/sub functionality."""
        publisher = None
        subscriber = None
        try:
            publisher = aioredis.Redis(**redis_config)
            subscriber = aioredis.Redis(**redis_config)

            channel = "test:channel"
            test_message = "Test message for pub/sub"

            # Subscribe to channel
            pubsub = subscriber.pubsub()
            await pubsub.subscribe(channel)

            # Wait for subscription confirmation
            message = await pubsub.get_message(timeout=1.0)
            assert message is not None, "Should receive subscription confirmation"
            assert message["type"] == "subscribe"

            # Publish a message
            await publisher.publish(channel, test_message)

            # Receive the published message
            message = await pubsub.get_message(timeout=5.0)
            assert message is not None, "Should receive published message"
            assert message["type"] == "message"
            assert message["data"] == test_message

            await pubsub.unsubscribe(channel)
            await pubsub.aclose()

        except Exception as e:
            pytest.fail(f"Redis pub/sub test failed: {e}")
        finally:
            if publisher:
                await publisher.aclose()
            if subscriber:
                await subscriber.aclose()

    @pytest.mark.asyncio
    async def test_redis_expiration(self, redis_config: dict):
        """Test Redis key expiration."""
        client = None
        try:
            client = aioredis.Redis(**redis_config)

            # Set key with short expiration
            test_key = "test:expire"
            await client.set(test_key, "expires_soon", ex=2)  # 2 seconds

            # Verify key exists
            value = await client.get(test_key)
            assert value == "expires_soon", "Key should exist initially"

            # Check TTL
            ttl = await client.ttl(test_key)
            assert ttl > 0, "Key should have positive TTL"
            assert ttl <= 2, "TTL should be <= 2 seconds"

            # Wait for expiration
            await asyncio.sleep(3)

            # Verify key expired
            value = await client.get(test_key)
            assert value is None, "Key should have expired"

        except Exception as e:
            pytest.fail(f"Redis expiration test failed: {e}")
        finally:
            if client:
                await client.aclose()


class TestCombinedDatabaseOperations:
    """Integration tests combining PostgreSQL and Redis."""

    @pytest.fixture
    def postgres_config(self) -> dict:
        """Get PostgreSQL configuration."""
        return {
            "host": os.getenv("POSTGRES_HOST", "postgres-test"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "horse_racing_test"),
            "user": os.getenv("POSTGRES_USER", "testuser"),
            "password": os.getenv("POSTGRES_PASSWORD", "testpass"),
        }

    @pytest.fixture
    def redis_config(self) -> dict:
        """Get Redis configuration."""
        return {
            "host": os.getenv("REDIS_HOST", "redis-test"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "db": int(os.getenv("REDIS_DB", "0")),
            "decode_responses": True,
        }

    @pytest.mark.asyncio
    async def test_cache_pattern(self, postgres_config: dict, redis_config: dict):
        """Test typical cache pattern with PostgreSQL and Redis."""
        pg_conn = None
        redis_client = None

        try:
            # Connect to both databases
            pg_conn = await asyncpg.connect(**postgres_config)
            redis_client = aioredis.Redis(**redis_config)

            # Create test table
            await pg_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS test_horses (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    track VARCHAR(100) NOT NULL,
                    odds DECIMAL(5,2)
                )
            """
            )

            # Insert test data
            horse_id = await pg_conn.fetchval(
                """
                INSERT INTO test_horses (name, track, odds)
                VALUES ($1, $2, $3)
                RETURNING id
            """,
                "Cache Test Horse",
                "Test Track",
                3.5,
            )

            cache_key = f"horse:{horse_id}"

            # First request - should hit database
            horse_data = await redis_client.get(cache_key)
            assert horse_data is None, "Cache should be empty initially"

            # Get from database
            horse = await pg_conn.fetchrow(
                """
                SELECT name, track, odds FROM test_horses WHERE id = $1
            """,
                horse_id,
            )

            # Cache the result
            horse_json = f"{horse['name']}|{horse['track']}|{horse['odds']}"
            await redis_client.set(cache_key, horse_json, ex=300)  # 5 min cache

            # Second request - should hit cache
            cached_data = await redis_client.get(cache_key)
            assert cached_data == horse_json, "Should retrieve from cache"

            # Clean up
            await redis_client.delete(cache_key)
            await pg_conn.execute("DELETE FROM test_horses WHERE id = $1", horse_id)

        except Exception as e:
            pytest.fail(f"Cache pattern test failed: {e}")
        finally:
            if pg_conn:
                await pg_conn.close()
            if redis_client:
                await redis_client.aclose()

    @pytest.mark.asyncio
    async def test_session_management(self, postgres_config: dict, redis_config: dict):
        """Test session management using Redis with PostgreSQL user data."""
        pg_conn = None
        redis_client = None

        try:
            pg_conn = await asyncpg.connect(**postgres_config)
            redis_client = aioredis.Redis(**redis_config)

            # Create users table
            await pg_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS test_users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100)
                )
            """
            )

            # Create test user
            user_id = await pg_conn.fetchval(
                """
                INSERT INTO test_users (username, email)
                VALUES ($1, $2)
                RETURNING id
            """,
                "testuser",
                "test@example.com",
            )

            # Create session
            session_id = f"session:{user_id}:abc123"
            session_data = {
                "user_id": str(user_id),
                "username": "testuser",
                "login_time": str(int(time.time())),
                "last_activity": str(int(time.time())),
            }

            # Store session in Redis
            await redis_client.hset(session_id, mapping=session_data)
            await redis_client.expire(session_id, 3600)  # 1 hour

            # Retrieve session
            retrieved_session = await redis_client.hgetall(session_id)
            assert retrieved_session["username"] == "testuser"
            assert retrieved_session["user_id"] == str(user_id)

            # Verify user exists in PostgreSQL
            user = await pg_conn.fetchrow(
                """
                SELECT username, email FROM test_users WHERE id = $1
            """,
                user_id,
            )
            assert user["username"] == "testuser"

            # Clean up
            await redis_client.delete(session_id)
            await pg_conn.execute("DELETE FROM test_users WHERE id = $1", user_id)

        except Exception as e:
            pytest.fail(f"Session management test failed: {e}")
        finally:
            if pg_conn:
                await pg_conn.close()
            if redis_client:
                await redis_client.aclose()
