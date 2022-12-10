import json
import os
import sys
import unittest

from pyfakefs import fake_filesystem_unittest

import app


class AppTest(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()
        os.makedirs('/Users/test/one/a', 0o755)
        with open('/Users/test/one/a/file', 'w') as f:
            f.write('foo')
        os.makedirs('/Users/test/two/.b', 0o644)
        with open('/Users/test/two/.b/.hidden', 'w') as f:
            f.write('bar')

        app.app.config['TESTING'] = True
        sys.argv = ['app.py', '-p', '/Users/test/']
        app.args = app.parse_args()
        self.app = app.app.test_client()

    def test_base_dir(self):
        response = self.app.get('/')
        assert 200 == response.status_code
        json_data = json.loads(response.get_data())
        self.assertEqual(2, len(json_data))

        self.assertEqual('one', json_data[0]['name'])
        self.assertEqual(501, json_data[0]['owner'])
        self.assertEqual('755', json_data[0]['permissions'])
        self.assertEqual(0, json_data[0]['size'])
        self.assertTrue(json_data[0]['isDir'])
        self.assertFalse(json_data[0]['isFile'])

        self.assertEqual('two', json_data[1]['name'])
        self.assertEqual(501, json_data[1]['owner'])
        self.assertEqual('644', json_data[1]['permissions'])
        self.assertEqual(0, json_data[1]['size'])
        self.assertTrue(json_data[1]['isDir'])
        self.assertFalse(json_data[1]['isFile'])

    def test_sub_dir(self):
        response = self.app.get('/one')
        assert 200 == response.status_code
        json_data = json.loads(response.get_data())
        self.assertEqual(1, len(json_data))

        self.assertEqual('a', json_data[0]['name'])
        self.assertEqual(501, json_data[0]['owner'])
        self.assertEqual('755', json_data[0]['permissions'])
        self.assertEqual(0, json_data[0]['size'])
        self.assertTrue(json_data[0]['isDir'])
        self.assertFalse(json_data[0]['isFile'])

    def test_dir_with_file(self):
        response = self.app.get('/one/a')
        assert 200 == response.status_code
        json_data = json.loads(response.get_data())
        self.assertEqual(1, len(json_data))

        self.assertEqual('file', json_data[0]['name'])
        self.assertEqual(501, json_data[0]['owner'])
        self.assertEqual('644', json_data[0]['permissions'])
        self.assertEqual(3, json_data[0]['size'])
        self.assertFalse(json_data[0]['isDir'])
        self.assertTrue(json_data[0]['isFile'])

    def test_dir_with_hidden_dir(self):
        response = self.app.get('/two')
        assert 200 == response.status_code
        json_data = json.loads(response.get_data())
        self.assertEqual(1, len(json_data))

        self.assertEqual('.b', json_data[0]['name'])
        self.assertEqual(501, json_data[0]['owner'])
        self.assertEqual('644', json_data[0]['permissions'])
        self.assertEqual(0, json_data[0]['size'])
        self.assertTrue(json_data[0]['isDir'])
        self.assertFalse(json_data[0]['isFile'])

    def test_dir_with_hidden_file(self):
        response = self.app.get('/two/.b')
        assert 200 == response.status_code
        json_data = json.loads(response.get_data())
        self.assertEqual(1, len(json_data))

        self.assertEqual('.hidden', json_data[0]['name'])
        self.assertEqual(501, json_data[0]['owner'])
        self.assertEqual('644', json_data[0]['permissions'])
        self.assertEqual(3, json_data[0]['size'])
        self.assertFalse(json_data[0]['isDir'])
        self.assertTrue(json_data[0]['isFile'])

    def test_file(self):
        response = self.app.get('/one/a/file')
        self.assertEqual(200, response.status_code)

        text = response.get_data().decode('utf-8')
        self.assertIn('foo', text)

    def test_hidden_file(self):
        response = self.app.get('/two/.b/.hidden')
        self.assertEqual(200, response.status_code)

        text = response.get_data().decode('utf-8')
        self.assertIn('bar', text)

    def test_missing_path(self):
        response = self.app.get('/three')
        self.assertEqual(404, response.status_code)

    def test_path_hack(self):
        # Make surer that a hacker cannot use .. to access files outside the
        # configured root directory.
        response = self.app.get('/../unsafedir')
        self.assertEqual(400, response.status_code)

    def test_swagger_spec(self):
        response = self.app.get('/api/spec')
        self.assertEqual(200, response.status_code)

        text = response.get_data().decode('utf-8')
        self.assertIn('FileEntry', text)

    # TODO: If this were production code, get the swagger UI working with the
    # test client to validate that it is present at /api/docs.


if __name__ == '__main__':
    unittest.main()
