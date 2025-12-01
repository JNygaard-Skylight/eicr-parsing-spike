import re

from lxml import etree

xml_file = "./schematron/eve_everywoman.xml"

# Simplify the XPath by specifying an alias for the namespace
namespaces = {"cda": "urn:hl7-org:v3"}
# There is a lot going on here but it is simply returning the code of the first planned order
# It is important to note that this is just my first guess of how APHL will specify the nonstandard code.
xpath= "/*[local-name()='ClinicalDocument' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='component' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='structuredBody' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='component' and namespace-uri()='urn:hl7-org:v3'][8]/*[local-name()='section' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='entry' and namespace-uri()='urn:hl7-org:v3'][3]/*[local-name()='organizer' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='component' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='observation' and namespace-uri()='urn:hl7-org:v3']"

tree = etree.parse(xml_file)

# `tree.xpath` returns a list, hopefully APHL would not give us an XPath that returned more tha 1.
elements = tree.xpath(xpath, namespaces=namespaces)

print(f"# of elements:\t{len(elements)}")

print(etree.tostring(elements[0], pretty_print=True).decode())
