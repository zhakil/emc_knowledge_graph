```markdown
# EMC Knowledge Graph Ontology

This document describes the ontology used for the EMC Knowledge Graph, including defined node labels, relationship types, and their key properties. This ontology is implemented in `services/knowledge_graph/emc_ontology.py`.

## Core Concepts

The ontology aims to model key entities and their interactions within the electromagnetic compatibility (EMC) domain. This includes standards, products, components, tests, test results, observed phenomena, regulations, and mitigation measures.

## Node Labels

The following node labels are defined:

| Label                       | Description                                                                 | Key Properties (from Dataclass)                                  |
| :-------------------------- | :-------------------------------------------------------------------------- | :--------------------------------------------------------------- |
| `EMCStandard`               | An EMC standard document (e.g., CISPR 32, IEC 61000-4-2).                   | `name`, `version`, `publication_date`, `category`                |
| `Product`                   | A piece of equipment or system being tested or considered (e.g., Laptop X). | `name`, `model_number`, `manufacturer`, `product_type`           |
| `Component`                 | A sub-part of a product (e.g., CPU, capacitor, shielding).                  | `name`, `part_number`, `manufacturer`, `component_type`          |
| `Test`                      | A specific EMC test performed (e.g., Radiated Emissions Test).              | `name`, `test_date`, `test_setup_description`                    |
| `TestResult`                | The outcome of a test (e.g., Pass, Fail, specific measurements).            | `name` (e.g., "Pass"), `value`, `margin`, `limit_value`          |
| `Frequency`                 | A specific frequency point (e.g., 100 MHz).                                 | `name` (e.g., "100MHz"), `value_hz`, `unit`                      |
| `FrequencyRange`            | A range of frequencies (e.g., 30MHz-1GHz).                                  | `name` (e.g., "30MHz-1GHz"), `min_value_hz`, `max_value_hz`      |
| `Phenomenon`                | An electromagnetic phenomenon (e.g., Radiated Emission, ESD).               | `name`, `phenomenon_type`                                        |
| `Regulation`                | A regulatory requirement or directive (e.g., FCC Part 15).                  | `name`, `jurisdiction`, `effective_date`                         |
| `MitigationMeasure`         | A technique or component used to mitigate EMC issues (e.g., Ferrite Bead).  | `name`, `measure_type`, `effectiveness_description`              |
| `Document`                  | A source document processed into the graph (e.g., test report, datasheet).  | `name` (filename/title), `file_id`, `document_type`, `author`    |
| `Organization`              | An entity like a test lab, manufacturer, or regulatory body.              | `name`, `organization_type`, `location`                          |
| `Equipment`                 | Test equipment used for performing EMC tests (e.g., Spectrum Analyzer).     | `name` (model), `equipment_type`, `serial_number`, `calibration_due_date` |

**Common Properties (in `BaseNode`):**
All nodes inherit these base properties:
*   `name`: (str) Primary identifier or common name for the node.
*   `description`: (Optional[str]) A textual description.
*   `source_document_ids`: (List[str]) IDs of source documents from which this node was extracted.
*   `properties`: (Dict[str, Any]) For additional, less structured data.

## Relationship Types

The following relationship types connect the nodes:

| Type                        | From Node(s)        | To Node(s)          | Description                                                              | Key Properties (from Dataclass)                     |
| :-------------------------- | :------------------ | :------------------ | :----------------------------------------------------------------------- | :-------------------------------------------------- |
| `APPLIES_TO`                | `EMCStandard`       | `Product`           | Indicates a standard is applicable to a product.                         | `conditions` (e.g., "For Class A equipment")        |
| `CONTAINS_COMPONENT`        | `Product`           | `Component`         | A product contains a specific component.                                 | `quantity` (optional)                               |
| `HAS_STANDARD`              | `Product`           | `EMCStandard`       | A product is designed or tested against a standard.                      |                                                     |
| `PERFORMED_TEST`            | `Product`           | `Test`              | A product underwent a specific test.                                     | `test_report_id` (optional)                         |
| `HAS_TEST_RESULT`           | `Test`              | `TestResult`        | A test has a specific result.                                            |                                                     |
| `OBSERVES_PHENOMENON`       | `TestResult`        | `Phenomenon`        | A test result is associated with an observed phenomenon.                 | `details` (e.g., specific emission levels)          |
| `REGULATES`                 | `Regulation`        | `Product`           | A regulation applies to a product category or type.                      |                                                     |
| `MITIGATES`                 | `MitigationMeasure` | `Phenomenon`        | A measure is used to mitigate a phenomenon.                              | `effectiveness_level` (optional)                    |
| `REFERENCES_STANDARD`       | `Document`          | `EMCStandard`       | A document references an EMC standard.                                   |                                                     |
| `MENTIONS_PRODUCT`          | `Document`          | `Product`           | A document mentions a product.                                           |                                                     |
| `USES_FREQUENCY`            | `Test`, `Product`   | `Frequency`         | A test or product operates at/uses a specific frequency.                 |                                                     |
| `HAS_FREQUENCY_RANGE`       | `Test`, `EMCStandard`| `FrequencyRange`    | A test is performed over, or a standard specifies, a frequency range.  |                                                     |
| `SPECIFIES_LIMIT`           | `EMCStandard`       | `Phenomenon`        | A standard specifies limits for a phenomenon.                            | `limit_value`, `frequency_range`, `detector_type`   |
| `CONDUCTED_BY`              | `Test`              | `Organization`      | A test was conducted by an organization (e.g., test lab).                |                                                     |
| `MANUFACTURED_BY`           | `Product`, `Component`| `Organization`      | A product/component was manufactured by an organization.                 |                                                     |
| `ISSUED_BY`                 | `Regulation`, `EMCStandard`| `Organization`| A regulation/standard was issued by an organization.                     |                                                     |
| `USES_EQUIPMENT`            | `Test`              | `Equipment`         | A test utilized specific test equipment.                                 |                                                     |
| `PART_OF`                   | `Component`         | `Product`           | A component is part of a larger product.                                 |                                                     |
|                             | `Frequency`         | `FrequencyRange`    | A specific frequency is part of a broader range.                         |                                                     |

**Common Relationship Properties (in `BaseRelationship`):**
All relationships can have these base properties:
*   `source_document_ids`: (List[str]) IDs of source documents from which this relationship was inferred.
*   `confidence_score`: (Optional[float]) A score indicating the confidence in the extracted relationship.
*   `properties`: (Dict[str, Any]) For additional, less structured data about the relationship.

## Using the Ontology

This ontology guides the entity extraction and relationship building processes. When new documents are processed, the system attempts to identify instances of these nodes and relationships to populate the Neo4j graph database. Queries against the graph can then leverage this structure to find insights and answer complex questions about EMC compliance, standards, and product characteristics.

*(Note: The full functionality of querying and populating the graph depends on the `Neo4jEMCService` which is currently under development and facing some tool-related implementation challenges.)*
```
