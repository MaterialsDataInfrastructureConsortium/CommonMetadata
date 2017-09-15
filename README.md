# CommonMetadata  

## About  

This package can be used to emit specific, schema-compliant metadata for various materials data services given a common metadata input.  Currently, the available services include the following:  

- [Citrine Informatics](https://citrine.io/)  
- [Materials Data Facility](https://materialsdatafacility.org/)  
- [Materials Commons](https://materialscommons.org/mcapp/#/data/home/top)  

## Installation  

### Requirements  

- Python >= 2.7.10 or >= 3.3  

### Setup  

$ pip install matmeta

## Usage

```python
from matmeta import payload_metaclass as pm
import json

def pprint_json(json_obj):
    print(json.dumps(json_obj, indent=4))
```

Figure out what needs to be included in the common metadata inputs.  

```python
input_template = pm.get_common_payload_template()
pprint_json(input_template)
```

The output (not shown) will provide a specification for input metadata.  Required fields must be provided.  Other fields can be provided if desired.  
  
The default for the `get_common_payload_template` function is to show requirements for all services.  To restrict the requirements, pass in a list of services, e.g. `pm.get_common_payload_template(services=['citrine', 'materials_commons', 'materials_data_facility'])`.  
  
View only required fields:  

```python
pprint_json(input_template['required_fields'])
```

```json
{
    "title": "string",
    "source": {
        "name": "string"
    },
    "data_contacts": [
        {
            "given_name": "string",
            "family_name": "string",
            "email": "string"
        }
    ],
    "data_contributors": [
        {
            "given_name": "string",
            "family_name": "string",
            "email": "string"
        }
    ],
    "links": {
        "landing_page": "uri (string)"
    },
    "description": "string"
}
```

Provide the required inputs: 

```python
inputs = {
    'data_contacts': [
        {
            'given_name': 'John',
            'family_name': 'Smith',
            'email': 'johnsmith@generic.org'
        }
    ],
    'data_contributors': [
        {
            'given_name': 'Jane',
            'family_name': 'Doe',
            'email': 'janedoe@generic.org'
        }
    ],
    'description': 'test description',
    'source': {
        'name': 'test source'
    },
    'title': 'test title',
    'links': {
        'landing_page': 'http://somepage.org'
    }
}
```

Now use the various metadata emitters.  

```python
citrine_metadata = pm.CITPayload(**inputs).metapayload
pprint_json(citrine_metadata)
```

```json
{
    "contacts": [
        {
            "tags": [
                "contact"
            ],
            "name": {
                "title": "",
                "given": "John",
                "family": "Smith"
            },
            "email": "johnsmith@generic.org"
        },
        {
            "tags": [
                "contributor"
            ],
            "name": {
                "title": "",
                "given": "Jane",
                "family": "Doe"
            },
            "email": "janedoe@generic.org"
        }
    ],
    "source": {
        "tags": []
    },
    "category": "system"
}
```

```python
mdf_metadata = pm.MDFPayload(**inputs).metapayload
pprint_json(mdf_metadata)
```

```json
{
    "mdf": {
        "title": "test title",
        "acl": [
            "public"
        ],
        "source_name": "test source",
        "links": {
            "landing_page": "http://somepage.org"
        },
        "data_contact": [
            {
                "given_name": "John",
                "family_name": "Smith",
                "email": "johnsmith@generic.org"
            }
        ],
        "data_contributor": [
            {
                "given_name": "Jane",
                "family_name": "Doe",
                "email": "janedoe@generic.org"
            }
        ],
        "description": "test description"
    },
    "dc": {}
}
```

```python
mc_metadata = pm.MCPayload(**inputs).metapayload
pprint_json(mc_metadata)
```

```json
{
    "name": "test source",
    "description": "test description"
}
```
