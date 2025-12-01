# eICR Parsing SPIKE
## Summary
We have been told that APHL will identify the nonstandard code by providing an XPath to the nonstandard code. We can then use that XPath to parse the eICR to retrieve the nonstandard code. while it is relatively trivial to parse XML with XPaths with Python, there are several potential complications we want to consider.

## XPath & Python
While Python's standard library does have the [xml.etree.ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html) it only supports a limited subset of XPath, therefore a 3rd party library will likely be needed. [lxml](https://pypi.org/project/lxml/) is widely used and supports XPath. In addition it has builtin security safeguards. While I think it would be safe to assume that by the time we are looking at the XML we can trust that it is not malicious, but it is nice to know if we are ever concerned with reading potentially untrustworthy XML.

## Schematron Output
While we will not know for certain what the XPaths given by APHL will look like until we get more information from them, we can run Schematron ourselves to get an idea of what it may look like. Setting up and running Schematron is a fairly annoying process, but if you are interested, here is the repo with the code I used.

I used Schematron to validate the [Eve Everywoman eICR](https://github.com/CDCgov/dibbs-FHIR-Converter/blob/main/data/SampleData/eCR/eCR_EveEverywoman.xml). While it is technically not an accurate representation of an eICR we would be handling, as it has already been through the process and has trigger code data, it should work to at least give us an idea of what Schematron will output. Running Schematron against the eICR we get this failed assertion in the output:

```xml
<svrl:failed-assert test="count(cda:code[@codeSystem='2.16.840.1.113883.6.1' or @nullFlavor])=1" id="a-1198-7133-v" location="/*[local-name()='ClinicalDocument' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='component' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='structuredBody' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='component' and namespace-uri()='urn:hl7-org:v3'][8]/*[local-name()='section' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='entry' and namespace-uri()='urn:hl7-org:v3'][3]/*[local-name()='organizer' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='component' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='observation' and namespace-uri()='urn:hl7-org:v3']">
  <svrl:text>SHALL contain exactly one [1..1] code, which SHOULD be selected from CodeSystem LOINC (urn:oid:2.16.840.1.113883.6.1) (CONF:1198-7133).</svrl:text>
</svrl:failed-assert>
```

Using the below script we can get the element identified with the XPath:
```python
import xml.etree.ElementTree as ET


xml_file = "./eve_everywoman.xml"

xpath= "//*[local-name()='ClinicalDocument' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='component' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='structuredBody' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='component' and namespace-uri()='urn:hl7-org:v3'][8]/*[local-name()='section' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='entry' and namespace-uri()='urn:hl7-org:v3'][3]/*[local-name()='organizer' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='component' and namespace-uri()='urn:hl7-org:v3']/*[local-name()='observation' and namespace-uri()='urn:hl7-org:v3']"

root = ET.parse(xml_file)

elements = root.findall(xpath)[0]

print(ET.tostring(elements[0]))
```
This gives us the following Observation:
```xml
<!-- Removed the copious comments for clarity. -->
<observation xmlns="urn:hl7-org:v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:cda="urn:hl7-org:v3" xmlns:sdtc="urn:hl7-org:sdtc"
  xmlns:voc="http://www.lantanagroup.com/voc" classCode="OBS" moodCode="EVN">
  <templateId root="2.16.840.1.113883.10.20.15.2.3.2" extension="2019-04-01" />
  <id root="bf9c0a26-4524-4395-b3ce-100450b9c9ac" />
  <code code="local_code_pertussis" codeSystem="2.16.840.1.113883.1.2.3.665"
    codeSystemName="local_coding_system"
    displayName="Bordetella pertussis in Throat by Organism specific culture">
    <translation code="548-8" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
      displayName="Bordetella pertussis [Presence] in Throat by Organism specific culture"
      sdtc:valueSet="2.16.840.1.114222.4.11.7508" sdtc:valueSetVersion="2020-11-13" />
  </code>
  <statusCode code="active" />
  <effectiveTime value="20201107" />
  <value xsi:type="CD" code="5247005" displayName="Bordetella pertussis (organism)"
    codeSystem="2.16.840.1.113883.6.96" codeSystemName="SNOMED CT"
    sdtc:valueSet="2.16.840.1.114222.4.11.7508" sdtc:valueSetVersion="2020-11-13" />
  <interpretationCode code="A" displayName="Abnormal" codeSystem="2.16.840.1.113883.5.83"
    codeSystemName="ObservationInterpretation" />
  <entryRelationship typeCode="COMP">
    <observation classCode="OBS" moodCode="EVN">
      <templateId root="2.16.840.1.113883.10.20.22.4.419" extension="2020-09-01" />
      <code code="92236-9" displayName="Laboratory Observation Result Status" codeSystemName="LOINC"
        codeSystem="2.16.840.1.113883.6.1" />
      <value xsi:type="CD" code="P" displayName="Preliminary results"
        codeSystem="2.16.840.1.113883.18.34"
        codeSystemName="HL7ObservationResultStatusCodesInterpretation" />
    </observation>
  </entryRelationship>
</observation>
```
We then can see that this observation does indeed have a nonstandard code:
```xml
<code code="local_code_pertussis" codeSystem="2.16.840.1.113883.1.2.3.665"
  codeSystemName="local_coding_system"
  displayName="Bordetella pertussis in Throat by Organism specific culture">
  <!-- removing the translation for clarity -->
</code>
```
Therefore until we get an actual example from APHL it seems reasonable to assume their XPaths will follow a similar form.

## Potential Issues
### XPaths Returning Multiple Elements
If the given XPath is coming from the output of Schematron I think it is safe to assume that it will indeed point to a single element, otherwise Schematron is significantly more useless than I realise.

### Relevant String Elsewhere
Say the above observation looks like:
```XML
<observation classCode="OBS" moodCode="RQO">
  <!-- [C-CDA R2.0] Planned Observation (V2) -->
  <templateId root="2.16.840.1.113883.10.20.22.4.44" extension="2014-06-09" />
  <id root="b52bee94-c34b-4e2c-8c15-5ad9d6def205" />
  <code nullFlavor="na">
    <originalText>
      local code for Zika test #1
    </originalText>
  <statusCode code="active" />
</observation>
```
Here, we do have a nonstandard code "test", but it contains no information regarding the type of test, and we would not be able to get meaningful results by embedding it. However we would likely get much better results if we instead used the `originalText` string. Therefore we would want logic to look for additional strings that may provide better results. Because of the extremely flexible nature of eICRs relevant strings could be any many different places, and our logic could potentially be quite involved. However I would suggest initially a fairly simple process of linearly checking known locations. As an example:
1) `observation.code.code`
2) `observation.code.translation.code`
3) `observation.code.originalText`
4) `observation.text`
5) `section.text` of containing element.

In addition we would need to look any references in any of the above locations. As example:
```XML
<section>
  <templateId root="2.16.840.1.113883.10.20.22.2.4.1" extension="2015-08-01" />
  <code code="8716-3" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
    displayName="Vital Signs" />
  <title>Vital Signs (Last Filed)</title>
  <text>
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Test Name</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>05/20/2014 7:36pm</td>
          <td>
            <content ID="SystolicBP_2">Systolic Blood Pressure 2</content>
          </td>
        </tr>
      </tbody>
    </table>
  </text>
  <entry typeCode="DRIV">
    <organizer classCode="CLUSTER" moodCode="EVN">
      <templateId root="2.16.840.1.113883.10.20.22.4.26" extension="2015-08-01" />
      <id root="e421f5c8-29c2-4798-9cb5-7988c236e49d" />
      <code code="46680005" displayName="Vital Signs"
        codeSystem="2.16.840.1.113883.6.96" codeSystemName="SNOMED CT">
      </code>
      <statusCode code="completed" />
      <effectiveTime value="20140520193605-0500" />
      <component>
        <observation classCode="OBS" moodCode="EVN">
          <templateId root="2.16.840.1.113883.10.20.22.4.27" />
          <templateId root="2.16.840.1.113883.10.20.22.4.27"
            extension="2014-06-09" />
          <id root="2721acc5-0d05-4402-9e62-79943ea3901c" />
          <code nullFlavor="na" /> <!--Bad Code-->
          <text>
            <reference value="#SystolicBP_2" />
          </text>
          <statusCode code="completed" />
          <effectiveTime value="20140520193605-0500" />
          <value xsi:type="PQ" value="120" unit="mm[Hg]" />
        </observation>
    </organizer>
  </entry>
</section>
```
In this example `observation.code` contains just a null flavor attribute. The `observation.text` contains a reference. If we search for the reference value `#SystolicBP_2` we will find it in the `section.text` containing the observation in question. The value we could use is then "Systolic Blood Pressure 2".
