import json
import xmltodict
import html


def find_keys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in find_keys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in find_keys(j, kv):
                yield x


def find_type_spec(spec_type, ref):
    for type in spec_type:
        if type['@IDENTIFIER'] == ref:
            # return type.keys()
            return type


def find_title_spec(xhtml):

    if '#text' in list(xhtml[2]['THE-VALUE']['div'].keys()):

        return xhtml[2]['THE-VALUE']['div']['#text']

    if 'p' in list(xhtml[2]['THE-VALUE']['div'].keys()):

        return xhtml[2]['THE-VALUE']['div']['p']


def find_enum_spec(type_object, spec_object):
    res = []

    for enum in spec_object['VALUES']['ATTRIBUTE-VALUE-ENUMERATION']:
        for ref_enum in type_object['SPEC-ATTRIBUTES']['ATTRIBUTE-DEFINITION-ENUMERATION']:
            try:
                if enum['DEFINITION']['ATTRIBUTE-DEFINITION-ENUMERATION-REF'] == ref_enum['@IDENTIFIER']:
                    if (ref_enum['@LONG-NAME'] != 'Artifact Format'):
                        res.append(
                            {ref_enum['@LONG-NAME']: find_enum_value(enum['VALUES']['ENUM-VALUE-REF'])})
            except:
                a = 1
    return res


def find_attr_def_string(spec_attr, attr_val_string):
    res = []

    for value in attr_val_string:
        for attr in spec_attr['ATTRIBUTE-DEFINITION-STRING']:
            if attr['@IDENTIFIER'] == value['DEFINITION']['ATTRIBUTE-DEFINITION-STRING-REF']:

                match attr['@LONG-NAME']:
                    case 'ReqIF.ForeignID':
                        res.append({
                            'Identifier': int(value['@THE-VALUE'])
                        })
                    case 'ReqIF.ForeignCreatedBy':
                        res.append({
                            'Creator': value['@THE-VALUE'],
                        })
                    case 'ReqIF.ForeignModifiedBy':
                        res.append({
                            'Contributor': value['@THE-VALUE'],
                        })

                    case _:
                        res.append({
                            attr['@LONG-NAME']: value['@THE-VALUE'],
                        })

    return res


def find_enum_value(ref_value):
    dt_def_enum = list(
        find_keys(data_dict, 'DATATYPE-DEFINITION-ENUMERATION'))[0]

    values = []
    for dt in dt_def_enum:
        for dump in dt['SPECIFIED-VALUES']['ENUM-VALUE']:
            values.append(dump)

    for value in values:
        if value['@IDENTIFIER'] == ref_value:
            return value['@LONG-NAME']


def find_title_and_text(spec_attr, attr_xhtml):

    res = []

    for value in attr_xhtml:
        for attr in spec_attr['ATTRIBUTE-DEFINITION-XHTML']:
            if value['DEFINITION']['ATTRIBUTE-DEFINITION-XHTML-REF'] == attr['@IDENTIFIER']:
                key = ''
                _value = value['THE-VALUE']
                match attr.get('@LONG-NAME'):
                    case 'ReqIF.Text':
                        key = 'ReqIF.Text'
                        _value = xmltodict.unparse(_value, pretty=True)[39:]

                    case 'ReqIF.Name':
                        key = 'Title'
                        _value = _value['div']['#text']
                    case 'ReqIF.ChapterName':
                        key = 'ReqIF.Text'
                        _value = xmltodict.unparse(_value, pretty=True)[39:]

                if key != '':
                    res.append({key: _value})

    return res


def find_time(spec_attr, attr_date):
    res = []
    for value in attr_date:
        for attr in spec_attr['ATTRIBUTE-DEFINITION-DATE']:
            if value['DEFINITION']['ATTRIBUTE-DEFINITION-DATE-REF'] == attr['@IDENTIFIER']:
                key = ''
                match attr['@LONG-NAME']:
                    case 'ReqIF.ForeignCreatedOn':
                        key = 'Created On'
                    case 'ReqIF.ForeignModifiedOn':
                        key = 'Modified On'

                if key != '':
                    res.append({key: value['@THE-VALUE']})

    return res


def zip_artifact(spec_object):

    res = {}

    spec_type = list(find_keys(dict(data_dict), 'SPEC-OBJECT-TYPE'))[0]

    type_ref = spec_object['TYPE']['SPEC-OBJECT-TYPE-REF']

    type_object = find_type_spec(spec_type, type_ref)

    res.update(
        {"Attribute Type": type_object['@LONG-NAME'], 'Description': ''})

    for a in find_attr_def_string(
            type_object['SPEC-ATTRIBUTES'], spec_object['VALUES']['ATTRIBUTE-VALUE-STRING']):
        res.update(a)

    for a in find_enum_spec(type_object, spec_object):
        res.update(a)

    for a in find_title_and_text(
            type_object['SPEC-ATTRIBUTES'], spec_object['VALUES']['ATTRIBUTE-VALUE-XHTML']):
        res.update(a)

    for a in find_time(type_object['SPEC-ATTRIBUTES'],
                       spec_object['VALUES']['ATTRIBUTE-VALUE-DATE']):
        res.update(a)

    return res

    # "Title": find_title_spec(spec_object['VALUES']['ATTRIBUTE-VALUE-XHTML']),


def convert_to_html(data):
    if isinstance(data, str):
        return html.escape(data)
    elif isinstance(data, list):
        return ''.join(convert_to_html(item) for item in data if item is not None)
    elif isinstance(data, dict):
        tag = list(data.keys())[0]
        attributes = data[tag]
        attributes_string = ' '.join(
            f'{k}="{v}"' for k, v in attributes.items())
        content = convert_to_html(attributes.get('#text'))
        return f"<{tag} {attributes_string}>{content}</{tag}>"
    else:
        return ''


data_dict = ""


def get_spec_object_ref_hierarchy(data, hierarchy=None):
    if hierarchy is None:
        hierarchy = []

    if isinstance(data, list):
        for item in data:
            get_spec_object_ref_hierarchy(item, hierarchy)
    elif isinstance(data, dict):
        object_ref = data.get("OBJECT", {}).get("SPEC-OBJECT-REF")
        if object_ref:
            hierarchy.append(object_ref)
        children = data.get("CHILDREN")
        if children:
            get_spec_object_ref_hierarchy(
                children.get('SPEC-HIERARCHY'), hierarchy)

    return hierarchy


if __name__ == '__main__':
    with open("example.xml") as xml_file:

        data_dict = xmltodict.parse(xml_file.read())
        # xml_file.close()

        # generate the object using json.dumps()
        # corresponding to json data

        spec = list(find_keys(data_dict, 'SPECIFICATIONS'))[0]['SPECIFICATION']

        module_name = spec['@LONG-NAME']

        module_type = list(
            find_keys(dict(data_dict), 'SPECIFICATION-TYPE'))[0]['@LONG-NAME']

        spec_objects = list(
            find_keys(dict(data_dict), 'SPEC-OBJECTS'))[0]['SPEC-OBJECT']

        list_artifact_info = []

        # print(list_hierarchy)

        data = get_spec_object_ref_hierarchy(
            spec['CHILDREN']['SPEC-HIERARCHY'])

        for id in data:

            for obj in spec_objects:
                if id == obj['@IDENTIFIER']:
                    # print(zip_artifact(obj))
                    list_artifact_info.append(zip_artifact(obj))

        json_data = json.dumps({
            "Module Name": module_name,
            "Module Type": module_type,
            "List Artifact Info": list_artifact_info
        })

        # json_data = json.dumps(data_dict)

        # Write the json data to output
        # json file
        with open("test.json", "w") as json_file:
            json_file.write(json_data)
            # json_file.close()
