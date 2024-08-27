# openaddresses-source-validator
To identify broken sources in OpenAddresses sources

The ides is to have a utility to identify the broken data sources in openaddresses sources, as there are sheer number of data sources manual verification of the same is quite a big task. This project is aimed at identifying the broken sources from the json files programmatically and publishing them on to a github page.

Currently the same is set up as a [github workflow](https://github.com/AjithGeorge/openaddresses-source-validator/actions/workflows/validator.yml)

The [github page]((https://ajithgeorge.github.io/openaddresses-source-validator/)
) is created just for convenience, the broken sources will be recorded in the logs and will be available as artifact of the workflow.

The github page allows for the quick review of the same.

## OA Source Validator Workflow
### Inputs

- **root_directory**: Directory to process (e.g., `openaddresses/sources/us/va/`). Any valid source directory available in openaddresses repo should be working here. The same can be triggered for the whole of US as `openaddresses/sources/us/`
- **publish_results**: Boolean to determine if results should be published to `gh-pages`. False- will process the sources and logs will be generated, but won't be published.

This workflow is manually triggered and helps in managing and publishing results based on processed data.

A simple ovierview of the flow chart is as:


 ![flow chart](flow-chart.png)