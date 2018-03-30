import json

from mock import patch, PropertyMock

from .test_main import BaseMainTestCase


class SLNRestfulTests(BaseMainTestCase):
    """ Testing the RESTful endpoints """
    def test_can_get_projects(self):
        class FakeTakens:
            @staticmethod
            def json():
                return [{
                    'id': 'taken1'
                }]

        with patch('star_logo_nova.sln_shared.get_or_create_bank') as MockBank:
            with patch('star_logo_nova.sln_shared.get_or_create_assessment_offered') as MockOffered:
                with patch('requests.get') as MockGet:
                    with patch('star_logo_nova.SLNProjects.serialize',
                               new_callable=PropertyMock) as MockSerialize:
                        MockBank.return_value = {
                            'id': 'bank'
                        }
                        MockOffered.return_value = {
                            'id': 'offered'
                        }
                        MockGet.return_value = FakeTakens
                        MockSerialize.return_value = [{
                            'id': 'taken1'
                        }]
                        url = '/api/projects'
                        req = self.app.get(url)
                        data = self.json(req)
                        assert len(data) == 1
                        assert data[0]['id'] == 'taken1'
                        assert MockBank.called
                        assert MockOffered.called
                        assert MockGet.called
                        assert MockSerialize.called

    def test_can_get_specific_project(self):
        with patch('star_logo_nova.sln_shared.get_or_create_bank') as MockBank:
            with patch('star_logo_nova.sln_shared.get_assessment_taken') as MockTaken:
                with patch('star_logo_nova.SLNProject.serialize',
                           new_callable=PropertyMock) as MockSerialize:
                    MockBank.return_value = {
                        'id': 'bank'
                    }
                    MockTaken.return_value = {
                        'id': 'taken'
                    }
                    MockSerialize.return_value = {
                        'id': 'taken2'
                    }
                    url = '/api/project/foo%3A1%40ODL'
                    req = self.app.get(url)
                    data = self.json(req)
                    assert data['id'] == 'taken2'
                    assert MockBank.called
                    assert MockTaken.called
                    assert MockSerialize.called

    def test_can_update_project(self):
        with patch('star_logo_nova.sln_shared.get_or_create_bank') as MockBank:
            with patch('star_logo_nova.sln_shared.update_assessment_taken') as MockTaken:
                with patch('star_logo_nova.SLNProject.serialize',
                           new_callable=PropertyMock) as MockSerialize:
                    MockBank.return_value = {
                        'id': 'bank'
                    }
                    MockTaken.return_value = {
                        'id': 'taken4'
                    }
                    MockSerialize.return_value = {
                        'id': 'taken6'
                    }
                    url = '/api/project/foo%3A2%40ODL'
                    payload = {
                        'title': 'foo',
                        'description': 'bar',
                        'project_str': '123x'
                    }
                    req = self.app.patch(
                        url,
                        params=json.dumps(payload),
                        headers={'content-type': 'application/json'})
                    self.ok(req)
                    data = self.json(req)
                    assert data['id'] == 'taken6'
                    assert MockBank.called
                    assert MockTaken.called
                    assert MockSerialize.called

    def test_can_remix_a_project(self):
        def side_effect(*args):
            data = args[3]
            assert 'user_id' in data
            assert '--' in data['user_id']
            assert 'provenanceId' in data
            assert data['provenanceId'] == 'foo%3A3%40ODL'
            return {
                'id': 'taken'
            }

        with patch('star_logo_nova.sln_shared.get_or_create_bank') as MockBank:
            with patch('star_logo_nova.sln_shared.get_or_create_assessment_offered') as MockOffered:
                with patch('star_logo_nova.sln_shared.create_assessment_taken',
                           autospec=True) as MockTaken:
                    with patch('star_logo_nova.SLNProject.serialize',
                               new_callable=PropertyMock) as MockSerialize:
                        MockBank.return_value = {
                            'id': 'bank'
                        }
                        MockOffered.return_value = {
                            'id': 'offered'
                        }
                        MockTaken.side_effect = side_effect
                        MockSerialize.return_value = {
                            'id': 'taken7'
                        }
                        url = '/api/project/foo%3A3%40ODL/remixes'
                        payload = {
                            'title': 'foo',
                            'description': 'bar',
                            'project_str': '123x'
                        }
                        req = self.app.post(
                            url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
                        self.ok(req)
                        data = self.json(req)
                        assert data['id'] == 'taken7'
                        assert MockBank.called
                        assert MockOffered.called
                        assert MockTaken.called
                        assert MockSerialize.called

    # pylint: disable=too-many-arguments
    @patch('star_logo_nova.SLNProject.serialize',
           new_callable=PropertyMock)
    @patch('star_logo_nova.sln_shared.create_assessment_taken',
           autospec=True)
    @patch('star_logo_nova.sln_shared.get_assessment_taken')
    @patch('star_logo_nova.sln_shared.get_or_create_assessment_offered')
    @patch('star_logo_nova.sln_shared.get_or_create_bank')
    def test_remixing_without_new_title_sets_default(self,
                                                     MockBank,
                                                     MockOffered,
                                                     MockGetTaken,
                                                     MockTaken,
                                                     MockSerialize):
        def side_effect(*args):
            data = args[3]
            assert 'user_id' in data
            assert '--' in data['user_id']
            assert 'provenanceId' in data
            assert data['provenanceId'] == 'foo%3A3%40ODL'
            assert 'title' in data
            assert data['title'] == 'Copy of taken-text'
            assert 'description' in data
            assert data['description'] == 'bar'
            return {
                'id': 'taken'
            }

        MockBank.return_value = {
            'id': 'bank'
        }
        MockOffered.return_value = {
            'id': 'offered'
        }
        MockGetTaken.return_value = {
            'id': 'taken2',
            'displayName': {
                'text': 'taken-text'
            },
            'description': {
                'text': 'taken-description'
            }
        }
        MockTaken.side_effect = side_effect
        MockSerialize.return_value = {
            'id': 'taken7'
        }
        url = '/api/project/foo%3A3%40ODL/remixes'
        payload = {
            'description': 'bar',
            'project_str': '123x'
        }
        req = self.app.post(
            url,
            params=json.dumps(payload),
            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        assert data['id'] == 'taken7'
        assert MockBank.called
        assert MockOffered.called
        assert MockGetTaken.called
        assert MockTaken.called
        assert MockSerialize.called

    # pylint: disable=too-many-arguments
    @patch('star_logo_nova.SLNProject.serialize',
           new_callable=PropertyMock)
    @patch('star_logo_nova.sln_shared.create_assessment_taken',
           autospec=True)
    @patch('star_logo_nova.sln_shared.get_assessment_taken')
    @patch('star_logo_nova.sln_shared.get_or_create_assessment_offered')
    @patch('star_logo_nova.sln_shared.get_or_create_bank')
    def test_remixing_without_new_description_sets_default(self,
                                                           MockBank,
                                                           MockOffered,
                                                           MockGetTaken,
                                                           MockTaken,
                                                           MockSerialize):
        def side_effect(*args):
            data = args[3]
            assert 'user_id' in data
            assert '--' in data['user_id']
            assert 'provenanceId' in data
            assert data['provenanceId'] == 'foo%3A3%40ODL'
            assert 'title' in data
            assert data['title'] == 'foo'
            assert 'description' in data
            assert data['description'] == 'taken-description'
            return {
                'id': 'taken'
            }

        MockBank.return_value = {
            'id': 'bank'
        }
        MockOffered.return_value = {
            'id': 'offered'
        }
        MockGetTaken.return_value = {
            'id': 'taken3',
            'displayName': {
                'text': 'taken-text'
            },
            'description': {
                'text': 'taken-description'
            }
        }
        MockTaken.side_effect = side_effect
        MockSerialize.return_value = {
            'id': 'taken7'
        }
        url = '/api/project/foo%3A3%40ODL/remixes'
        payload = {
            'title': 'foo',
            'project_str': '123x'
        }
        req = self.app.post(
            url,
            params=json.dumps(payload),
            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        assert data['id'] == 'taken7'
        assert MockBank.called
        assert MockOffered.called
        assert MockGetTaken.called
        assert MockTaken.called
        assert MockSerialize.called

    def test_can_create_a_new_project(self):
        def side_effect(*args):
            data = args[3]
            assert 'user_id' in data
            assert '--' in data['user_id']
            return {
                'id': 'taken'
            }

        with patch('star_logo_nova.sln_shared.get_or_create_bank') as MockBank:
            with patch('star_logo_nova.sln_shared.get_or_create_assessment_offered') as MockOffered:
                with patch('star_logo_nova.sln_shared.create_assessment_taken',
                           autospec=True) as MockTaken:
                    with patch('star_logo_nova.SLNProject.serialize',
                               new_callable=PropertyMock) as MockSerialize:
                        MockBank.return_value = {
                            'id': 'bank'
                        }
                        MockOffered.return_value = {
                            'id': 'offered'
                        }
                        MockTaken.side_effect = side_effect
                        MockSerialize.return_value = {
                            'id': 'taken5'
                        }
                        url = '/api/projects'
                        payload = {
                            'title': 'foo',
                            'description': 'bar',
                            'project_str': '123x'
                        }
                        req = self.app.post(
                            url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
                        self.ok(req)
                        data = self.json(req)
                        assert data['id'] == 'taken5'
                        assert MockBank.called
                        assert MockOffered.called
                        assert MockTaken.called
                        assert MockSerialize.called