from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import redis
import time

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379)

@app.route('/api/<user_id>', methods=['GET'])
def handle_request(user_id):
    # Retrieve the request count for the user_id from Redis
    request_count = r.get(f'request_count:{user_id}')

    # If the request count exists in Redis
    if request_count is not None:
        request_count = int(request_count)
        # Check if the request count exceeds the limit (100 in this example)
        if request_count >= 100:
            return jsonify({'message': 'Request limit exceeded. Throttled.'}), 429

        # Update the request count in Redis
        r.incr(f'request_count:{user_id}')

    else:
        # Set the initial request count for the user_id in Redis
        r.set(f'request_count:{user_id}', 1)

    # Process the request and return the response
    # ...

    return jsonify({'message': 'Request processed successfully.'})

def update_count():
    # Get the current timestamp in seconds
    timestamp = int(time.time())
    # Get the count for the specified timestamp
    cnt_60_before = r.zscore('request_counts', timestamp - 60)
    count_value = r.get('count')
    r.set('count_key', count_value - cnt_60_before)

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_count, 'interval', seconds=1)  # Run the task every 1 second
    scheduler.start()
    app.run(host='0.0.0.0', port=8080)
