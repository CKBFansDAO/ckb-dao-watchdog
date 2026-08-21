import unittest

import metaforo_watchdog_cn as cn
import metaforo_watchdog_en as en


class MetaforoHeadersTest(unittest.TestCase):
    def test_browser_metadata_is_present_without_cookie(self):
        required = {
            "sec-ch-ua",
            "sec-ch-ua-mobile",
            "sec-ch-ua-platform",
            "sec-fetch-dest",
            "sec-fetch-mode",
            "sec-fetch-site",
        }

        for module in (cn, en):
            with self.subTest(module=module.__name__):
                self.assertTrue(required <= module.METAFORO_HEADERS.keys())
                self.assertNotIn("cookie", module.METAFORO_HEADERS)


if __name__ == "__main__":
    unittest.main()
