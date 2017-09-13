import datetime


class PublishablePayload(dict):
    def __init__(self, title, source_name, data_contact, data_contributor, links, **kwargs):
        """

        Parameters
        ----------
        title:              str
        source_name:        str
        data_contact:       Human
        data_contributor:   Human
        links:              dict
        """
        super(PublishablePayload, self).__init__()
        self.__dict__ = self

        optionalkeys = ['license',  # str
                        'citation',  # list of str
                        'source_name',  # str
                        'data_contact',  # human
                        'data_contributor',  # human
                        'author',  # human
                        'repository',  # str
                        'collection',  # str
                        'tags',  # list of str
                        'description',  # str
                        'raw',  # str
                        'links',  # dict
                        'year',  # int
                        'composition']  # str
        for prop in optionalkeys:
            self[prop] = kwargs.get(prop, None)

        self['title'] = title
        self['source_name'] = source_name
        self['data_contact'] = data_contact
        self['data_contributor'] = data_contributor
        self['links'] = links

    @property
    def metapayload(self):
        raise NotImplementedError


class CITPayload(PublishablePayload):
    pass


class MDFPayload(PublishablePayload):
    """

    Examples
    --------
    >>> scripty = Human(given_name='Totally', family_name='NotARobot', email='a@a.com', institution='Earth')
    >>> payload = MDFPayload(title='Test Payload', source_name='Doctest Example Script', data_contact=scripty, data_contributor=scripty, links={'landing_page':'http://www.globus.org'})
    >>> payload.metapayload
    {'mdf': {'title': 'Test Payload', 'acl': [], 'source_name': 'Doctest Example Script', 'citation': None, 'links': {'landing_page': 'http://www.globus.org'}, 'data_contact': {'given_name': 'Totally', 'family_name': 'NotARobot', 'email': 'a@a.com', 'institution': 'Earth'}, 'data_contributor': {'given_name': 'Totally', 'family_name': 'NotARobot', 'email': 'a@a.com', 'institution': 'Earth'}, 'ingest_date': 'Sep 13, 2017', 'metadata_version': '1.1', 'mdf_id': '1', 'resource_type': 'dataset'}, 'dc': {}, 'misc': {}}

    """

    def __init__(self, *args, **kwargs):
        super(MDFPayload, self).__init__(*args, **kwargs)

    @property
    def metapayload(self):
        dataset = {
            "mdf": {
                "title": self.title,
                "acl": [],  # TODO: what goes here?
                "source_name": self.source_name,
                "citation": self.citation,
                "links": self.links,
                "data_contact": [dict(data_contact) for data_contact in self.data_contacts],
                "data_contributor": [dict(data_contributor) for data_contributor in self.data_contributors],
                "ingest_date": datetime.datetime.now().strftime('%b %d, %Y'),  # TODO: shouldn't this be implied?
                "metadata_version": "1.1",
                "mdf_id": "1",
                "resource_type": "dataset"
            },
            "dc": {},
            "misc": {}
        }

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
