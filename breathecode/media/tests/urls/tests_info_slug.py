"""
Test /answer
"""
import re, urllib
from unittest.mock import patch
from django.urls.base import reverse_lazy
from rest_framework import status
from breathecode.tests.mocks import (
    GOOGLE_CLOUD_PATH,
    apply_google_cloud_client_mock,
    apply_google_cloud_bucket_mock,
    apply_google_cloud_blob_mock,
)
from ..mixins import MediaTestCase


class MediaTestSuite(MediaTestCase):
    """Test /answer"""
    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    def test_info_id_without_auth(self):
        """Test /answer without auth"""
        url = reverse_lazy('media:info_slug', kwargs={'media_slug': 'they-killed-kenny'})
        response = self.client.get(url)
        json = response.json()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    def test_info_id_wrong_academy(self):
        """Test /answer without auth"""
        url = reverse_lazy('media:info_slug', kwargs={'media_slug': 'they-killed-kenny'})
        response = self.client.get(url, **{'HTTP_Academy': 1})
        json = response.json()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    def test_info_id_without_capability(self):
        """Test /cohort/:id without auth"""
        self.headers(academy=1)
        url = reverse_lazy('media:info_slug', kwargs={'media_slug': 'they-killed-kenny'})
        self.generate_models(authenticate=True)
        response = self.client.get(url)
        json = response.json()

        self.assertEqual(json, {
            'detail': "You (user: 1) don't have this capability: read_media for academy 1",
            'status_code': 403
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    def test_info_id_without_data(self):
        """Test /answer without auth"""
        self.headers(academy=1)
        models = self.generate_models(authenticate=True,
                                      profile_academy=True,
                                      capability='read_media',
                                      role='potato')
        url = reverse_lazy('media:info_slug', kwargs={'media_slug': 'they-killed-kenny'})
        response = self.client.get(url)
        json = response.json()

        self.assertEqual(json, {'detail': 'Media not found', 'status_code': 404})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.all_media_dict(), [])

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    def test_root(self):
        """Test /answer without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     capability='read_media',
                                     role='potato',
                                     media=True)
        url = reverse_lazy('media:info_slug', kwargs={'media_slug': model['media'].slug})
        response = self.client.get(url)
        json = response.json()

        self.assertEqual(
            json, {
                'categories': [],
                'hash': model['media'].hash,
                'hits': model['media'].hits,
                'id': model['media'].id,
                'mime': model['media'].mime,
                'name': model['media'].name,
                'slug': model['media'].slug,
                'thumbnail': f'{model.media.url}-thumbnail',
                'url': model['media'].url
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_media_dict(), [{**self.model_to_dict(model, 'media')}])

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    def test_info_id_with_category(self):
        """Test /answer without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     capability='read_media',
                                     role='potato',
                                     media=True,
                                     category=True)
        url = reverse_lazy('media:info_slug', kwargs={'media_slug': model['media'].slug})
        response = self.client.get(url)
        json = response.json()
        self.print_model(model, 'media')
        self.print_model(model, 'category')

        self.assertEqual(
            json, {
                'categories': [{
                    'id': 1,
                    'medias': 1,
                    'name': model['category'].name,
                    'slug': model['category'].slug,
                }],
                'hash':
                model['media'].hash,
                'hits':
                model['media'].hits,
                'id':
                model['media'].id,
                'mime':
                model['media'].mime,
                'name':
                model['media'].name,
                'slug':
                model['media'].slug,
                'thumbnail':
                f'{model.media.url}-thumbnail',
                'url':
                model['media'].url
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_media_dict(), [{**self.model_to_dict(model, 'media')}])
