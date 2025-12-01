from pathlib import Path

from lxml import etree


class FileResolver(etree.Resolver):
    def resolve(self, url: str, pubid, context):
        if not (url.startswith(("/", "schematron"))):
            url = f"{Path.cwd()}/schematron/{url}"
        return self.resolve_filename(url, context)


eicr_file = Path("eve_everywoman.xml")
schema_file = Path("schema.sch")
xsl = Path("schematron/iso_svrl_for_xslt1.xsl")


parser = etree.XMLParser()
parser.resolvers.add(FileResolver())

schematron_doc = etree.parse(schema_file, parser)
iso_xslt = etree.parse(xsl, parser)
transform = etree.XSLT(iso_xslt)
validator_xslt = transform(schematron_doc)

validator = etree.XSLT(validator_xslt)
ccda_doc = etree.parse(eicr_file, parser)

result = validator(ccda_doc)

result.write("./output.xml", pretty_print=True)
