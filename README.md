# py-rate-limiter

Used to keep track of rate limited APIs such as Foursquare, Facebook
and Instagram. It estimates how often the API should be hit so that
the requests are distributed evenly till the end of the hour when
the limit is being reset.

The new rate can be sent to a callback if it deviates more than a 
sensitivity value (hits per second) from the last callback call. 

Sample usage:

```python

def print_new_rate(hps):
    print "New hits per second: {hps}".format(hps=hps)

hits_per_minute_sensitivity = 5.0
hits_per_second_sensitivity = hits_per_minute_sensitivity / 60.0

limiter = RateLimiter(hits_per_second_sensitivity, print_new_rate)

def task_that_periodically_connects_to_an_api():
    response = api.request()
    total_limit = response.headers['X-RateLimit-Limit']
    remaining_limit = response.headers['X-RateLimit-Remaining']

    limiter.update(total_limit, remaining_limit)
```