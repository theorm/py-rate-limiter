from datetime import datetime, timedelta

SECONDS_IN_HOUR = 60 * 60


class RateLimiter(object):
    ''' Used to keep track of rate limited APIs such as Foursquare, Facebook
        and Instagram. It estimates how often the API should be hit so that
        the requests are distributed evenly till the end of the hour when
        the limit is being reset.

        The new rate can be sent to a callback if it deviates more than a 
        sensitivity value (hits per second) from the last callback call. 

        Sample usage:
        ------------

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

    '''

    '''If set to `True`, will ignore updates where total_hits == remaining_hits.
    '''
    ignore_equals = False

    def __init__(self, hits_per_second_sensitivity=None, callback=None, ignore_equals=False):
        self.reset()
        self.set_callback(hits_per_second_sensitivity, callback)
        self.ignore_equals = ignore_equals
        
    def reset(self, reset_time=None):
        self._total_hits = 0
        self._remaining_hits = 0
        self._last_updated = datetime.now()
        self._last_reset = reset_time if reset_time else datetime.now()
        self._last_hits_per_second = 0

    @property
    def rate_limit(self):
        return self._total_hits, self._remaining_hits

    def set_callback(self, hits_per_second_sensitivity, callback):
        ''' Set callback function that will be called when rate
            changes more than `hits_per_second_sensitivity` since
            last time callback was invoked.
        '''
        self._hits_sensitivity = hits_per_second_sensitivity
        self._callback = callback

    def _estimate_reset_time(self, total, remaining):
        '''If it's the first call to update()
        we will try to estimate reset time based on average api hit rate.
        '''
        hits_done = total - remaining
        average_hit_per_second_rate = float(total) / float(SECONDS_IN_HOUR)
        seconds_elapsed = hits_done * average_hit_per_second_rate

        self._last_reset = datetime.now() - timedelta(seconds=seconds_elapsed)

    def update(self, total_hits, remaining_hits):
        ''' Update limiter with rate limit and remaining limit from the 
            API and calculate new speed based rate limit.
        '''
        if total_hits == remaining_hits and self.ignore_equals:
            return

        if datetime.now() - self._last_updated > timedelta(hours=1):
            # last time the limiter was updated was more than an hour ago
            # so we reset it
            self.reset()

        if self._total_hits == 0 and total_hits != 0:
            self._estimate_reset_time(total_hits, remaining_hits)

        self._total_hits = total_hits
        self._last_remaining_hits = self._remaining_hits
        self._remaining_hits = remaining_hits

        self._calculate_and_invoke_callback()
        self._last_updated = datetime.now() 

    def _next_reset(self):
        return self._last_reset + timedelta(hours=1)

    def _calculate_and_invoke_callback(self):
        if self._remaining_hits > self._last_remaining_hits:
            # we've got into new hour
            self._last_reset = datetime.now()

        time_left_till_next_reset = self._next_reset() - datetime.now()

        # calculate rate that we should use to evenly distribute hits to the api till the end of the period
        current_hits_per_second = float(self._remaining_hits) / float(time_left_till_next_reset.total_seconds())
        
        # print '%s = %s / %s' % (current_hits_per_second, float(self._remaining_hits), float(time_left_till_next_reset.total_seconds()))

        if self._callback and self._hits_sensitivity:
            # print ('diff: %s, threshold: %s' % (abs(self._last_hits_per_second - current_hits_per_second), self._hits_sensitivity))
            if self._last_hits_per_second == 0 or (abs(self._last_hits_per_second - current_hits_per_second) > self._hits_sensitivity):
                # invoke callback as we got off the sensitivity limits
                # print 'new hps %s' % current_hits_per_second
                self._last_hits_per_second = current_hits_per_second
                self._callback(current_hits_per_second)

