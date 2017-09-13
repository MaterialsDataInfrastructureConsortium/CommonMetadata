from ..payload_metaclass import *


def test_metapayload():
    scripty = Human(given_name='Totally', family_name='NotARobot', email='a@a.com', institution='Earth')
    kwargs = dict(title='Test Payload',
                  source={'name': 'whatever', 'producer': 'test producer', 'url': 'http://www.testurl.org',
                          'tags': ['these', 'are', 'source', 'tags']}, data_contacts=[scripty],
                  data_contributors=[scripty], links={'landing_page': 'http://www.globus.org'}, licenses=[
            {'name': 'license name', 'url': 'http://www.licenseurl.org', 'description': 'license description',
             'tags': ['license', 'tags']}, ])

    citpayload = CITPayload(**kwargs)
    mdfpayload = MDFPayload(**kwargs)
    mcpayload = MCPayload(**kwargs)

    for payload in [citpayload, mdfpayload, mcpayload]:
        assert payload.metapayload
