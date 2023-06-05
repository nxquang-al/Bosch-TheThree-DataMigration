import xmltodict


def find_keys(node, kv):
    """
    The function recursively searches for a specific key in a nested dictionary and returns its value.

    :param node: The node parameter is the current node being searched in the recursive function. It can
    be either a dictionary or a list
    :param kv: kv stands for "key value" and is a parameter that represents the key that we want to
    search for in a nested dictionary or list. The function "find_keys" recursively searches through the
    nested structure and yields the values associated with the specified key
    """
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


if __name__ == '__main__':
    data_dict = xmltodict.parse(open('./Requirements.reqif').read())

    print(len(list(find_keys(data_dict, 'SPEC-OBJECT'))))
