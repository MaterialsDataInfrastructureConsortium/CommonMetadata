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
    return {} # no metadata is required


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
        'links': {
            'landing_page': 'uri (string)'
        },
    }


def _validate_inputs(actual_inputs, required_inputs, keypath=None):
    """
    Validate inputs.  Raise exception if something is missing.

    args:
        actual_inputs:  the object/dictionary passed to a subclass of 
            PublishablePayload
        required_inputs: the object/dictionary containing keys (and subkeys)
            for required fields.  (See get_common_payload_template.)
        keypath: used internally in recursive function calls.

    return:
        Nothing.  An exception will be raised if a problem is encountered.
    """
    actual_keys = set(actual_inputs.keys())
    required_keys = set(required_inputs.keys())
    if actual_keys.intersection(required_keys) != required_keys:
        prefix = '%s.' if keypath else ''
        output_keys = {'%s%s' % (prefix, key) for key in required_keys}
        raise Exception("Missing input fields.  Expected %s." % ', '.join(output_keys))
    for key in required_keys:
        # TODO: review the following usage of isinstance.
        # Will this always be appropriate, given duck typing?
        if isinstance(required_inputs[key], dict):
            new_keypath = key if not keypath else '%s.%s' % (keypath, key)
            _validate_inputs(
                actual_inputs=actual_inputs[key],
                required_inputs=required_inputs[key],
                keypath=new_keypath
            )


def _citation_to_string(citation):
    """
    Convert citation object to a string, using standard citation formatting.  

    args:
        citation:   a dictionary potentially containing all fields from
            pypif.obj.Reference, and possibly a few others

    TODO: This is tedious and fragile.  Find a better way to get 'er done.
    TODO: This function assumes that citations are either to books or journals.
        urls are ignored.

    references: 
        http://citrineinformatics.github.io/pif-documentation/schema_definition/common/Reference.html
        http://www.scientificstyleandformat.org/Tools/SSF-Citation-Quick-Guide.html

    journals:
        format:     Author(s). Date. Article title. Journal title. Volume(issue):location.
        example:    Mazan MR, Hoffman AM. 2001. Effects of aerosolized albuterol on physiologic 
                         responses to exercise in standardbreds. Am J Vet Res. 62(11):1812–1817.

    books:
        format:     Author(s). Date. Title. Edition. Place of publication: publisher. Extent. Notes.
        example:    Leboffe MJ, Pierce BE. 2010. Microbiology: laboratory theory and application. 
                        Englewood (CO): Morton Publishing Company.
    """
    output = ''
    sep = '. '

    if 'authors' in citation:
        authors = []
        for author in citation['authors']:
            if 'family_name' not in author:
                continue
            author_name = author['family_name']
            if 'given_name' in author:
                author_name += ' ' + author['given_name']
            authors.append(author_name)
        output += ', '.join(authors) + sep
    if 'year' in citation:
        output += str(citation['year']) + sep
    if 'title' in citation:
        output += citation['title'] + sep

    if 'journal' in citation:
        output += citation['journal'] + sep
        if 'volume' in citation:
            output += citation['volume']
            if 'issue' in citation:
                output += '(' + citation['issue'] + ')'
            if 'page_location' in citation:
                output += ':' + citation['page_location'] + sep
    else:   # assume for now that the reference is to a book
            # TODO(Handle url case.)
        if 'edition' in citation:
            output += citation['edition'] + sep
        if 'publication_location' in citation:
            output += citation['publication_location']
            if 'publisher' in citation:
                output += ': ' + citation['publisher'] + sep
        elif 'publisher' in citation:
            output += citation['publisher'] + sep
        if 'extent' in citation:
            output += citation['extent'] + sep
        if 'notes' in citation:
            output += citation['notes'] + sep

    return output.strip()


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
            'links': {
                'landing_page': 'uri (string)',
                'publication': ['uri (string)'],
                'data_doi': 'uri (string)',
                'related_id': ['string'],
                'parent_id': 'string'
            },
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
            'citations': [
                {
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
                    'year': 'string',
                    'title': 'string',
                    'journal': 'string',
                    'volume': 'string',
                    'issue': 'string',
                    'page_location': 'string',
                    'edition': 'string',
                    'publication_location': 'string',
                    'publisher': 'string',
                    'extent': 'string',
                    'notes': 'string',
                }
            ],
            'repository': 'not yet available',
            'collection': 'not yet available',
            'tags': ['string'],
            'description': 'string',
            'raw': 'not yet available',
            'year': 'integer',
            'composition': 'not yet available'
        },
        'required_fields': combined_requirements,
        'usage': 'payload = <service class, e.g. CITPayload>(**input_dictionary).metapayload'
    }


class PublishablePayload(dict):
    def __init__(self, **kwargs):
        """
        TODO: write more!!
        TODO: consider making this an abstract base class (package abc).
        """
        self.__dict__ = self
        super(PublishablePayload, self).__init__()
        for key in get_common_payload_template()['all_fields'].keys():
            if key in kwargs:
                self[key] = kwargs[key]

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
        required_inputs = get_common_payload_template(services=['citrine'])['required_fields']
        _validate_inputs(
            required_inputs=required_inputs,
            actual_inputs=kwargs
        )
        super(CITPayload, self).__init__(**kwargs)        

    @property
    def metapayload(self):
        metadata = pobj.System()
        self._add_source(metadata)
        self._add_people(metadata)
        self._add_licenses(metadata)
        self._add_citations(metadata)
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
    
    def _add_citations(self, metadata):
        if 'citations' not in self or not isinstance(self['citations'], list):
            return 
        # Note: the citrine type is 'Reference', not 'Citation'.
        # http://citrineinformatics.github.io/pif-documentation/schema_definition/common/Reference.html
        citrine_citation_fields = {
            'doi', 'isbn', 'issn', 'url', 'title', 'publisher', 'journal',
            'volume', 'issue', 'year', 'figure', 'table', 'pages', 'authors', 
            'editors', 'affiliations', 'acknowledgements', 'referenes', 'tags'
        }
        # Note: the citrine type is 'Name', not 'Author'.
        # http://citrineinformatics.github.io/pif-documentation/schema_definition/common/Name.html
        citrine_author_fields = {
            'title', 'given', 'family', 'suffix', 'tags'
        }
        citrine_citations = []
        for citation in self['citations']:
            filtered_citation_data = {
                key: citation[key] for key in citation
                if key in citrine_citation_fields
            }
            authors = []
            if 'authors' in filtered_citation_data:
                for author in filtered_citation_data['authors']:
                    # fix name keys
                    if 'given_name' in author:
                        author['given'] = author['given_name']
                    if 'family_name' in author:
                        author['family'] = author['family_name']
                    # filter keys
                    filtered_author_data = {
                        key: author[key] for key in author
                        if key in citrine_author_fields
                    }
                    citrine_author = pobj.Name(**filtered_author_data)
                    authors.append(citrine_author)
            citrine_citation = pobj.Reference(**filtered_citation_data)
            citrine_citation.authors = authors
            citrine_citations.append(citrine_citation)
        metadata.references = citrine_citations


class MDFPayload(PublishablePayload):
    """

    Examples
    --------
    >>> scripty = Human(given_name='Totally', family_name='NotARobot', email='a@a.com', institution='Earth')
    >>> payload = MDFPayload(title='Test Payload', source={'name': 'Doctest Example Script'}, data_contacts=[scripty], data_contributors=[scripty], links={'landing_page':'http://www.globus.org'}, description='some material')
    >>> payload.metapayload
    {'Doctest Example Script': {}, 'dc': {}, 'mdf': {'acl': ['public'],  'citations': None,  'data_contact': [{'email': 'a@a.com', 'family_name': 'NotARobot', 'given_name': 'Totally', 'institution': 'Earth'}], 'data_contributor': [{'email': 'a@a.com', 'family_name': 'NotARobot', 'given_name': 'Totally', 'institution': 'Earth'}], 'links': {'landing_page': 'http://www.globus.org'}, 'source_name': 'Doctest Example Script', 'title': 'Test Payload'}}

    """

    def __init__(self, *args, **kwargs):
        required_inputs = get_common_payload_template(services=['materials_data_facility'])['required_fields']
        _validate_inputs(
            required_inputs=required_inputs,
            actual_inputs=kwargs
        )
        super(MDFPayload, self).__init__(*args, **kwargs)

    @property
    def metapayload(self):
        dataset = {
            "mdf": {
                "title": self.title,
                "acl": ["public"],  # TODO: allow list of globus auth uuids or "public"
                "source_name": self.source['name'],
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
            # # TODO: review the following.
            # self.source['name']: self.additionalProperties
        }

        # Populate optional keys if they have been set
        required_keys = set(
            get_common_payload_template(
                services=['materials_data_facility']
            )['required_fields'].keys()
        )
        optional_keys = set(
            get_common_payload_template()['all_fields'].keys()
        ) -  required_keys
        for key in optional_keys:
            if key in {'citations'}:
                continue
            if key in self and self[key] is not None:
                dataset['mdf'][key] = self[key]
        if 'citations' in self:
            dataset['mdf']['citation'] = [
                _citation_to_string(citation)
                for citation in self['citations']
            ]

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
        required_inputs = get_common_payload_template(services=['materials_commons'])['required_fields']
        _validate_inputs(
            required_inputs=required_inputs,
            actual_inputs=kwargs
        )
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
