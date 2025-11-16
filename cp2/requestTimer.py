import requests
import time

URL = 'http://localhost:5000'

def time_request(url):
    start_time = time.time()
    response = requests.get(f"{url}")
    end_time = time.time()
    elapsed_time = end_time - start_time
    return response.status_code, elapsed_time

def endpoint_statistics(url):
    timings = []
    for _ in range(5):
        status_code, elapsed_time = time_request(url)
        timings.append(elapsed_time)
    average_time = sum(timings) / len(timings)
    median_time = sorted(timings)[len(timings) // 2]
    stdev_time = (sum((x - average_time) ** 2 for x in timings) / len(timings)) ** 0.5
    return average_time, min(timings), max(timings), median_time, stdev_time

if __name__ == "__main__":
    endpoints = ['/data', '/dl/stat/mean', '/dl/stat/peak']
    for endpoint in endpoints:
        url = URL + endpoint
        avg, min_time, max_time, median, stdev = endpoint_statistics(url)
        print(f"Endpoint: {endpoint}")
        print(f"  Average Time: {avg:.4f} seconds")
        print(f"  Min Time: {min_time:.4f} seconds")
        print(f"  Max Time: {max_time:.4f} seconds")
        print(f"  Median Time: {median:.4f} seconds")
        print(f"  Standard Deviation: {stdev:.4f} seconds\n")
        print("-" * 40)