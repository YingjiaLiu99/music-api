import unittest
import json
import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to sys.path to find the 'application' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from application import app 


class TestApiRecommend(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_recommend_with_valid_playlist(self): 
        # using the testing spotify url
        valid_playlist_url = "https://open.spotify.com/playlist/0L8R5SEpmdZLuYAz5WXf4n?si=4b7c01a91d1d4f1f"

        response = self.app.get('/api/recommend', query_string={'playlist_url': valid_playlist_url})
        self.assertEqual(response.status_code, 200)        
        data = json.loads(response.data)
        self.assertIn('recommendations', data)

    def test_recommend_with_invalid_playlist(self):
        invalid_playlist_url = "https://open.spotify.com/playlist/INVALID"
        response = self.app.get('/api/recommend', query_string={'playlist_url': invalid_playlist_url})
        self.assertNotEqual(response.status_code, 200)

    def test_recommend_without_playlist(self):  
        response = self.app.get('/api/recommend')   
        self.assertEqual(response.status_code, 400)


class TestBatchApiRecommend(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_batch_recommend_with_valid_urls(self):
        payload = {
            'playlist_urls': [
                "https://open.spotify.com/playlist/0L8R5SEpmdZLuYAz5WXf4n?si=4b7c01a91d1d4f1f",
                "https://open.spotify.com/playlist/7cKhUkOOqRWgmLmVTFL462?si=a124c9a59dbd4b8c"
            ],
            'number_of_recs': 5
        }
        response = self.app.post('/api/batch_recommend', json=payload)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)  

    def test_batch_recommend_with_some_invalid_urls(self):
        payload = {
            'playlist_urls': [
                "https://open.spotify.com/playlist/0L8R5SEpmdZLuYAz5WXf4n?si=4b7c01a91d1d4f1f",
                "https://open.spotify.com/playlist/INVALID"
            ]
        }
        response = self.app.post('/api/batch_recommend', json=payload)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertIn('error', data[1]) 

    def test_batch_recommend_without_urls(self):
        payload = {
            'playlist_urls': []
        }
        response = self.app.post('/api/batch_recommend', json=payload)
        self.assertEqual(response.status_code, 400)

    def test_batch_recommend_with_specified_number_of_recs(self):
        payload = {
            'playlist_urls': [
                "https://open.spotify.com/playlist/0L8R5SEpmdZLuYAz5WXf4n?si=4b7c01a91d1d4f1f"
            ],
            'number_of_recs': 3
        }
        response = self.app.post('/api/batch_recommend', json=payload)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(all(len(reco['recommendations']) <= 3 for reco in data))  # check if number of recs is as specified

class TestApiCreatePlaylist(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_create_playlist_without_token(self):
        response = self.app.post('/api/playlist/create', data=json.dumps({'playlist_url': 'https://open.spotify.com/playlist/0L8R5SEpmdZLuYAz5WXf4n?si=4b7c01a91d1d4f1f'}), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Spotify token is required', response.json['error'])


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add tests to the test suite
    suite.addTests(loader.loadTestsFromTestCase(TestApiRecommend))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchApiRecommend))
    
    # include create playlist to the test suite
    suite.addTests(loader.loadTestsFromTestCase(TestApiCreatePlaylist))

    with open("api_test_results.txt", "w") as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        runner.run(suite)