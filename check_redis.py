import redis

try:
    # Create a Redis client
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # Try to ping the Redis server
    response = r.ping()
    if response:
        print("[SUCCESS] Redis is running and accessible!")
        print("Connection successful on localhost:6379")
    else:
        print("[ERROR] Redis is not responding properly")
except redis.ConnectionError:
    print("[ERROR] Could not connect to Redis")
    print("Please make sure Redis is installed and running")
except Exception as e:
    print(f"[ERROR] An error occurred: {str(e)}")
