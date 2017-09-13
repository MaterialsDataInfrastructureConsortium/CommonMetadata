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
import datetime


class PublishablePayload(dict):
    def __init__(self, title, source, data_contacts, data_contributors, links, **kwargs):
        """
        Parameters
        ----------
        title:              str
        source:             dict: { 'name': str, 'producer': str, 'url': str, 'tags': list(str)}
        data_contact:       Human
        data_contributor:   Human
        links:              dict
        """
        super(PublishablePayload, self).__init__()
        self.__dict__ = self

        self._optionalkeys = ['licenses',    # list of dicts: {
                                            #     'name': str,
                                            #     'description': str,
                                            #     'url': str,
                                            #     'tags': list of str
                                            # }
                              'citations',  # list of str
                              'authors',  # list of human
                              'repository',  # str
                              'collection',  # str
                              'tags',  # list of str
                              'description',  # str
                              'raw',  # str
                              'links',  # dict
                              'year',  # int
                              'composition']  # str
        for prop in self._optionalkeys:
            self[prop] = kwargs.get(prop, None)

        # validate the source parameter 
        # (require MDF field (name), but not the citrine fields)
        expected_source_keys = ['name',]
        for key in expected_source_keys:
            if key not in source:
                raise Exception('source requires a %s field' % key)

        self['title'] = title
        self['source'] = source
        self['data_contacts'] = data_contacts
        self['data_contributors'] = data_contributors
        self['links'] = links
        self['additionalProperties'] = kwargs

    def get_common_payload_template(self):
        """
        Get a template dictionary that can be used to create a payload object.

        TODO: implement
        """
        return {
            'template': {
                'title': 'string',
                'source': {
                    'name': 'string',
                    'producer': 'string',
                    'url': 'url string',
                    'tags': ['string']
                },
                'data_contacts': [
                    {
                        'given_name': 'string',
                        'family_name': 'string',
                        'title': 'string',
                        'orcid': 'TBD',
                        'email': 'TBD',
                        'tags': ['string']
                    }
                ],
                'data_contributors': [
                    {
                        'given_name': 'string',
                        'family_name': 'string',
                        'title': 'string',
                        'orcid': 'TBD',
                        'email': 'TBD',
                        'tags': ['string']
                    }
                ],
                'links': 'TBD',
                'authors': [
                    {
                        'given_name': 'string',
                        'family_name': 'string',
                        'title': 'string',
                        'orcid': 'TBD',
                        'email': 'TBD',
                        'tags': ['string']
                    }
                ],
                'licenses': [
                    {
                        'name': 'string',
                        'description': 'string',
                        'url': 'string',
                        'tags': ['string']
                    }
                ],
                'citations': 'TBD',
                'repository': 'TBD',
                'collection': 'TBD',
                'tags': ['string'],
                'description': 'string',
                'raw': 'TBD',
                'year': 'integer',
                'composition': 'TBD'
            },
            'required': [
                'title', 
                'source (name only)', 
                'data_contacts', 
                'data_contributors', 
                'links'
            ],
            'usage': 'payload = <PublishablePayload_subclass>(**input_dictionary); metadata = payload.metapayload'
        }


    @property
    def metapayload(self):
        raise NotImplementedError

    def ingest(self):
        raise NotImplementedError


class CITPayload(PublishablePayload):
    """
    Construct payload for POST call to Citrine service.

    Implemented fields (so far) include contacts and source.  
    These roughly correspond to the fields required by MDF.

    Examples
    --------
    >>> scripty = Human(given_name='Totally', family_name='NotARobot', email='a@a.com', institution='Earth')
    >>> payload = CITPayload(title='Test Payload', source={'name': 'whatever', 'producer': 'test producer', 'url': 'http://www.testurl.org', 'tags': ['these', 'are', 'source', 'tags']}, data_contacts=[scripty], data_contributors=[scripty], links={'landing_page':'http://www.globus.org'}, licenses=[{'name': 'license name', 'url': 'http://www.licenseurl.org', 'description': 'license description', 'tags': ['license', 'tags']},])
    >>> payload.metapayload
    {'email': 'a@a.com', 'name': {'family': 'NotARobot', 'given': 'Totally', 'title': ''}, 'tags': ['contributor']}], 'licenses': [{'description': 'license description', 'name': 'license name', 'tags': ['license', 'tags'], 'url': 'http://www.licenseurl.org'}], 'source': {'producer': 'test producer', 'tags': ['these', 'are', 'source', 'tags'], 'url': 'http://www.testurl.org'}}

    """

    def __init__(self, *args, **kwargs):
        super(CITPayload, self).__init__(*args, **kwargs)        
        self.metadata = pobj.System()
        self._add_source()
        self._add_people()
        self._add_licenses()

    @property
    def metapayload(self):
        return json.loads(pif.dumps(self.metadata))

    def _add_source(self):
        if 'producer' in self['source']:
            producer = self['source']['producer']
        if 'url' in self['source']:
            url = self['source']['url']
        if 'tags' in self['source']:
            tags = self['source']['tags']

        self.metadata.source = pobj.Source(
            producer=producer,
            url=url,
            tags=tags
        )

    def _add_people(self):
        people = []
        
        def add_to_people(person_list, tags):
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
                
        if 'authors' in self and isinstance(self['authors'], list):
            add_to_people(person_list=self['authors'], tags=['author'])
        if 'data_contacts' in self and isinstance(self['data_contacts'], list):
            add_to_people(person_list=self['data_contacts'], tags=['contact'])
        if 'data_contributors' in self and isinstance(self['data_contributors'], list):
            add_to_people(person_list=self['data_contributors'], tags=['contributor'])
        
        self.metadata.contacts = people

    def _add_licenses(self):
        if 'licenses' not in self or not isinstance(self['licenses'], list):
            return

        citrine_licenses = []

        for license in self['licenses']:
            try:
                citrine_license = pobj.License(**license)
                citrine_licenses.append(citrine_license)
            except Exception as ex:
                print(ex)

        self.metadata.licenses = citrine_licenses


class MDFPayload(PublishablePayload):
    """

    Examples
    --------
    >>> scripty = Human(given_name='Totally', family_name='NotARobot', email='a@a.com', institution='Earth')
    >>> payload = MDFPayload(title='Test Payload', source={'name': 'Doctest Example Script'}, data_contacts=[scripty], data_contributors=[scripty], links={'landing_page':'http://www.globus.org'})
    >>> payload.metapayload
    {'Doctest Example Script': {}, 'dc': {}, 'mdf': {'acl': ['public'],  'citations': None,  'data_contact': [{'email': 'a@a.com', 'family_name': 'NotARobot', 'given_name': 'Totally', 'institution': 'Earth'}], 'data_contributor': [{'email': 'a@a.com', 'family_name': 'NotARobot', 'given_name': 'Totally', 'institution': 'Earth'}], 'links': {'landing_page': 'http://www.globus.org'}, 'source_name': 'Doctest Example Script', 'title': 'Test Payload'}}

    """

    def __init__(self, *args, **kwargs):
        super(MDFPayload, self).__init__(*args, **kwargs)

    @property
    def metapayload(self):
        dataset = {
            "mdf": {
                "title": self.title,
                "acl": ["public"],  # TODO: allow list of globus auth uuids or "public"
                "source_name": self.source['name'],
                "citations": self.citations,
                "links": self.links,
                "data_contact": self.data_contacts,
                "data_contributor": [dict(data_contributor) for data_contributor in self.data_contributors],
                # "ingest_date": datetime.datetime.now().strftime('%b %d, %Y'),  # Note: these commented keys are
                # "metadata_version": "1.1",                                     # populated automatically!
                # "mdf_id": "1",
                # "resource_type": "dataset",
                # "additionalProperties": self.additionalProperties
            },
            "dc": {},  # TODO: allow datacite keys to go here?
            # TODO: review the following.
            self.source['name']: self.additionalProperties
        }

        # Populate optional keys if they have been set
        for key in self._optionalkeys:
            val = getattr(self, key)
            if val is not None:
                dataset['mdf'][key] = val

        return dataset



class MCPayload(PublishablePayload):
    pass


class Human(dict):
    def __init__(self, given_name, family_name, email='', institution=''):
        super(Human, self).__init__()
        self.__dict__ = self
        self['given_name'] = given_name
        self['family_name'] = family_name
        self['email'] = email
        self['institution'] = institution
