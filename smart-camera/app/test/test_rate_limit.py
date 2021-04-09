from unittest import TestCase
from unittest.mock import Mock, patch
from time import time, sleep
from utils.rate_limit import rate_limited


class RateLimitTestCase(TestCase):
    def setUp(self) -> None:
        pass

    def test_rate_limited_one_call(self):
        func = Mock()
        rate = rate_limited(1, block=False)
        wrap = rate(func)

        param = {'parameter': True}
        wrap(param)
        wrap(param)

        func.assert_called_once_with(param)

    def test_rate_limited_multiple_calls(self):
        func = Mock()
        rate = rate_limited(1, block=False)
        wrap = rate(func)

        wrap()

        sleep(1)
        wrap()
        self.assertEqual(func.call_count, 2)

        func.reset_mock()

        with patch('time.time') as time_mock:
            time_mock.return_value = time() + 1 # 1 second
            wrap()
            self.assertEqual(func.call_count, 1)

            time_mock.return_value = time() + 2
            wrap()
            self.assertEqual(func.call_count, 2)


    def test_rate_limited_multiple_calls_blocking(self):
        func = Mock()
        rate = rate_limited(10, block=True)
        wrap = rate(func)

        wrap()
        wrap()

        self.assertEqual(func.call_count, 2)
