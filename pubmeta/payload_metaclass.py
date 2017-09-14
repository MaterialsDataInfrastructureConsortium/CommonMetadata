"""
Extract metadata for three materials data publication services from a common payload.

Services:
    Citrine:                    <link>
    Materials Data Facility:    <link>
    Materials Commons:          <link>

TODO: move service metadata requirements (as specified in the output of 
the get_common_payload_metadata function) to a config file.
"""

from pypif import pif
import pypif.obj as pobj
import json
import datetime


def _citrine_metadata_requirements():
    return None


def _materials_commons_metadata_requirements():
    return {
        'source': {
            'name': 'string'
        },
        'description': 'string'
    }


def _materials_data_facility_metadata_requirements():
    return {
        'title': 'string',
        'source': {
            'name': 'string',
        },
        'data_contacts': [
            {
                'given_name': 'string',
                'family_name': 'string',
                'email': 'string',
            }
        ],
        'data_contributors': [
            {
                'given_name': 'string',
                'family_name': 'string',
                'email': 'string',
            }
        ],
    }

def get_common_payload_template(services=None):
    """
    Get a template dictionary that can be used to create a payload object.

    TODO: services s/b a list. Specify required fields for each service in list.
        None means all services.
    """
    available_services = {'citrine', 'materials_commons', 'materials_data_facility'}
    if services is None:
        services = list(available_services)
    else:
        services = [service for service in services if service in available_services]
        if not services:
            services = list(available_services)
    combined_requirements = {}
    for service in services:
        # TODO(Recursive check dictionaries to make sure all requirements fields are combined.)
        service_requirements = eval('_%s_metadata_requirements()' % service)
        if service_requirements:
            for key in service_requirements:
                if not key in combined_requirements:
                    combined_requirements[key] = service_requirements[key]
    return {
        'all_fields': {
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
                    'email': 'string',
                    'tags': ['string']
                }
            ],
            'data_contributors': [
                {
                    'given_name': 'string',
                    'family_name': 'string',
                    'title': 'string',
                    'orcid': 'TBD',
                    'email': 'string',
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
                    'email': 'string',
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
        'required_fields': combined_requirements,
        'usage': 'payload = <service class, e.g. CITPayload>(**input_dictionary).metapayload'
    }


class PublishablePayload(dict):
    def __init__(self, **kwargs):
        """
        TODO: write more!!

        Inheriting subclasses can define self._required_keys before running base class __init__ to validate. 
        """
        self.__dict__ = self
        self._required_keys = [] # Overriden by subclass
        super(PublishablePayload, self).__init__()

        for key in self._required_keys:
            if key not in kwargs:
                raise Exception("%s requires %s" % (self.__class__.__name__, key))
                del kwargs[key]

        self._optionalkeys = get_common_payload_template()['all_fields'].keys()
        for prop in self._optionalkeys:
            self[prop] = kwargs.get(prop, None)
            if prop in kwargs: del kwargs[prop]

        # All properties that are not required or optional go to additionalProperties
        self.additionalProperties = kwargs

    @property
    def metapayload(self):
        raise NotImplementedError

    def ingest(self):
        raise NotImplementedError


class CITPayload(PublishablePayload):
    """
    Construct payload for POST call to Citrine service.

    Examples
    --------
    >>> scripty = Human(given_name='Totally', family_name='NotARobot', email='a@a.com', institution='Earth')
    >>> payload = CITPayload(title='Test Payload', source={'name': 'whatever', 'producer': 'test producer', 'url': 'http://www.testurl.org', 'tags': ['these', 'are', 'source', 'tags']}, data_contacts=[scripty], data_contributors=[scripty], links={'landing_page':'http://www.globus.org'}, licenses=[{'name': 'license name', 'url': 'http://www.licenseurl.org', 'description': 'license description', 'tags': ['license', 'tags']},])
    >>> payload.metapayload
    {'email': 'a@a.com', 'name': {'family': 'NotARobot', 'given': 'Totally', 'title': ''}, 'tags': ['contributor']}], 'licenses': [{'description': 'license description', 'name': 'license name', 'tags': ['license', 'tags'], 'url': 'http://www.licenseurl.org'}], 'source': {'producer': 'test producer', 'tags': ['these', 'are', 'source', 'tags'], 'url': 'http://www.testurl.org'}}

    """

    def __init__(self, *args, **kwargs):
        self._required_keys = [] # Citrine has no metadata requirements.
        super(CITPayload, self).__init__(**kwargs)        

    @property
    def metapayload(self):
        metadata = pobj.System()
        self._add_source(metadata)
        self._add_people(metadata)
        self._add_licenses(metadata)
        return json.loads(pif.dumps(metadata))

    def _add_source(self, metadata):
        if 'source' not in self or not isinstance(self['source'], dict):
            return

        if 'producer' in self['source']:
            producer = self['source']['producer']
        else:
            producer = None
        if 'url' in self['source']:
            url = self['source']['url']
        else:
            url = None
        if 'tags' in self['source']:
            tags = self['source']['tags']
        else:
            tags = []

        metadata.source = pobj.Source(
            producer=producer,
            url=url,
            tags=tags
        )

    def _add_people(self, metadata):
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
        
        metadata.contacts = people

    def _add_licenses(self, metadata):
        if 'licenses' not in self or not isinstance(self['licenses'], list):
            return

        citrine_licenses = []

        for license in self['licenses']:
            try:
                citrine_license = pobj.License(**license)
                citrine_licenses.append(citrine_license)
            except Exception as ex:
                print(ex)

        metadata.licenses = citrine_licenses


class MDFPayload(PublishablePayload):
    """

    Examples
    --------
    >>> scripty = Human(given_name='Totally', family_name='NotARobot', email='a@a.com', institution='Earth')
    >>> payload = MDFPayload(title='Test Payload', source={'name': 'Doctest Example Script'}, data_contacts=[scripty], data_contributors=[scripty], links={'landing_page':'http://www.globus.org'}, description='some material')
    >>> payload.metapayload
    {'Doctest Example Script': {}, 'dc': {}, 'mdf': {'acl': ['public'],  'citations': None,  'data_contact': [{'email': 'a@a.com', 'family_name': 'NotARobot', 'given_name': 'Totally', 'institution': 'Earth'}], 'data_contributor': [{'email': 'a@a.com', 'family_name': 'NotARobot', 'given_name': 'Totally', 'institution': 'Earth'}], 'links': {'landing_page': 'http://www.globus.org'}, 'source_name': 'Doctest Example Script', 'title': 'Test Payload'}}

    """

    def __init__(self, **kwargs):
        # TODO(Get required keys for each service from a config file (.ini).)
        self._required_keys = ['title', 'source', 'data_contacts', 'data_contributors', 'links']
        super(MDFPayload, self).__init__(**kwargs)
        if not isinstance(kwargs['source'], dict):
            raise Exception('source must be a dictionary')
        if 'name' not in self['source']:
            raise Exception('source must contain "name"')

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
    """
    Examples
    --------
    >>> scripty = Human(given_name='Totally', family_name='NotARobot', email='a@a.com', institution='Earth')
    >>> payload = MCPayload(title='Test Payload', source={'name': 'whatever', 'producer': 'test producer', 'url': 'http://www.testurl.org', 'tags': ['these', 'are', 'source', 'tags']}, data_contacts=[scripty], data_contributors=[scripty], links={'landing_page':'http://www.globus.org'}, licenses=[{'name': 'license name', 'url': 'http://www.licenseurl.org', 'description': 'license description', 'tags': ['license', 'tags']},], description='material description')
    >>> payload.metapayload
    {'description': 'material description', 'name': 'whatever'}

    """

    def __init__(self, *args, **kwargs):
        # TODO(Get required keys for each service from a config file (.ini).)
        self._required_keys = ['name', 'description']
        super(MCPayload, self).__init__(*args, **kwargs)

    @property
    def metapayload(self):
        return {
            'name': self['source']['name'],
            'description': self['description']
        }


class Human(dict):
    def __init__(self, given_name, family_name, email='', institution=''):
        super(Human, self).__init__()
        self.__dict__ = self
        self['given_name'] = given_name
        self['family_name'] = family_name
        self['email'] = email
        self['institution'] = institution
