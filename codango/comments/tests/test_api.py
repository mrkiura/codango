from rest_framework import status
from rest_framework.test import APITestCase

message = {"detail":
           "Authentication credentials were not provided."}

class CommentTest(APITestCase):
    def test_comment(self):
        response = self.client.get('/api/v1/comments/')
        self.assertEqual(response.data, message)
        self.assertNotEqual(response.data, {})
        self.assertEqual(response.status_code, 401)
