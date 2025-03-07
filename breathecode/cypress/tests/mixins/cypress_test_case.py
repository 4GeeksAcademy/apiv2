"""
Collections of mixins used to login in authorize microservice
"""
import os

from rest_framework.test import APITestCase

from breathecode.tests.mixins import (CacheMixin, DatetimeMixin, GenerateModelsMixin, GenerateQueriesMixin,
                                      HeadersMixin, ICallMixin)


class CypressTestCase(APITestCase, GenerateModelsMixin, CacheMixin, GenerateQueriesMixin, HeadersMixin,
                      DatetimeMixin, ICallMixin):
    """AdmissionsTestCase with auth methods"""
    def setUp(self):
        self.generate_queries()
        os.environ['API_URL'] = 'http://localhost:8000'

    def tearDown(self):
        self.clear_cache()
