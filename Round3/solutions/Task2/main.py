import argparse
import json
from RstBuilder import RstBuilder
from HTMLParser import MyHTMLParser
from tqdm import tqdm

def init_argument():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--input_file", help="Directory to input file. Accepts file *.json only")
    parser.add_argument("-o", "--output_file",
                        help="Directory to output *.rst file.")

    args = parser.parse_args()

    return args.input_file, args.output_file

if __name__ == '__main__':
    INP_SRC, OUT_SRC = init_argument()
    data = json.load(open(INP_SRC))
    doc = RstBuilder(open(OUT_SRC, 'w'))

    doc.newline()
    doc.title(data['Module Name'])
    doc.newline()

    for artifact in tqdm(data['List Artifact Info']):
        if artifact['Attribute Type'] == 'Heading':
            doc.heading(artifact['Title'])
            doc.newline()
        else:
            fields = [
                ('id', str(artifact['Identifier'])),
                ('artifact_type', str(artifact['Attribute Type'])),
            ]
            if artifact['Attribute Type'] != 'Information':
                fields.extend([
                    ('crq', artifact['CRQ']),
                    ('artifact_type', str(artifact['Attribute Type'])),
                    ('variant', artifact['VAR_FUNC_SYS']),
                    ('allocation', artifact['Allocation']),
                    ('status', str(artifact['Status'])),
                    ('safety_level', artifact['Safety Classification']),
                    ('verify', artifact['Verification Criteria']),
                ])

            doc.directive('sw_req', fields)
            parser = MyHTMLParser()
            parser.feed(artifact['ReqIF.Text'])
            doc.content(parser.get_rst())
            parser.close()
