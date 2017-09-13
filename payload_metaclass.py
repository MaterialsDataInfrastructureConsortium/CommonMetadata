"""
Extract metadata for three materials data publication services from a common payload.

Services:
    Citrine:                    <link>
    Materials Data Facility:    <link>
    Materials Commons:          <link>
"""

from pypif import pif
import pypif.obj as pobj
import json


class PublishablePayload(dict):
    def __init__(self, **kwargs):
        """
        Parameters
        ----------
        title:              str
        source_name:        str
        data_contact:       human
        data_contributor:   human
        links:              dict
        """
        super(PublishablePayload, self).__init__()
        self.__dict__ = self
        
        required_keys = [
            'title',                  # str
            'source_name',            # str
            'data_contacts',          # list of human
            'data_contributors',      # list of human
            'links'                   # dict
        ]
        
        for key in required_keys:
            if key not in kwargs:
                raise Exception("%s is a required parameter" % key)
            self[key] = kwargs[key]

        optional_keys = [
            'license',                 # str
            'citation',                # list of str
            'authors',                 # list of human
            'repository',              # str
            'collection',              # str
            'tags',                    # list of str
            'description',             # str
            'raw',                     # str
            'year',                    # int
            'composition'              # str
        ]
        
        for key in optional_keys:
            self[key] = kwargs.get(key, None)
    

class CITPayload(PublishablePayload):
    def __init__(self, **kwargs):
        super(CITPayload, self).__init__()
        metadata = pobj.System()
        self._add_source(metadata)
        self._add_people(metadata)
        self.__dict__ = json.loads(pif.dumps(metadata))

    def _add_source(self, metadata):
        pass

    def _add_people(self, metadata):
        people = []
        
        def add_to_list(person_list, tags):
            for person in person_list:
                citrine_name_info = {
                    'given': person.get('given_name', ''),
                    'family': person.get('family_name', ''),
                    'title': person.get('title', ''),
                }
                citrine_name = pobj.Name(**citrine_name_info)
                citrine_person_info = {
                    'name': citrine_name,
                    'orcid': person.get('orcid', None),
                    'email': person.get('email', None),
                    'tags': tags
                }
                citrine_person = pobj.Person(**citrine_person_info)
                people.append(citrine_person)
                
        if 'authors' in self:
            add_to_list(person_list=self['authors'], tags=['author'])
        if 'data_contacts' in self:
            add_to_list(person_list=self['data_contacts'], tags=['contact'])
        if 'data_contributors' in self:
            add_to_list(person_list=self['data_contributors'], tags=['contributor'])
        
        metadata.contacts = people


class MDFPayload(PublishablePayload):
    pass


class MCPayload(PublishablePayload):
    pass


class human(dict):
    def __init__(self, given_name, family_name, email='', institution=''):
        super(human, self).__init__()
        self.__dict__ = self

