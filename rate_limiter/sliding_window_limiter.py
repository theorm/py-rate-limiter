from .limiter import RateLimiter
from datetime import timedelta, datetime

class SlidingWindowLimiter(RateLimiter):
    '''Rate limiter for a hourly sliding window.
    '''

    def reset(self, reset_time=None):
        self._total_hits = 0
        self._remaining_hits = 0
        self._last_updated = datetime.now()
        self._last_hits_per_second = 0

    def update(self, total_hits, remaining_hits):
        ''' Update limiter with rate limit and remaining limit from the 
            API and calculate new speed based rate limit.
        '''
        if total_hits == remaining_hits and self.ignore_equals:
            return

        self._total_hits = total_hits
        self._last_remaining_hits = self._remaining_hits
        self._remaining_hits = remaining_hits

        self._calculate_and_invoke_callback()
        self._last_updated = datetime.now() 

    def _calculate_and_invoke_callback(self):

        # hits_left_percents = (float(self._remaining_hits) / float(self._total_hits)) * 100

        # calculate rate that we should use to evenly distribute hits to the api till the end of the period
        current_hits_per_second = float(self._remaining_hits) / float(timedelta(hours=1).total_seconds())

        if self._callback and self._hits_sensitivity:
            if self._last_hits_per_second == 0 or (abs(self._last_hits_per_second - current_hits_per_second) > self._hits_sensitivity):
                # invoke callback as we got off the sensitivity limits
                self._last_hits_per_second = current_hits_per_second
                self._callback(current_hits_per_second)
