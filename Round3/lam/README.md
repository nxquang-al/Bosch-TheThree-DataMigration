# Configuration File Usage Guide

This guide provides instructions on how to use the atribute name and attribute value when migrate data from reqif to json and from json to rst.

## Reqif to Json Configuration

The module configuration section allows you to define different modules with their associated properties.

### Module Name
Format config:
```yaml
module:
  name:
    key: {json key of module name}
    value_type: {type}
    value_mapping:
      {old value}: {new value}
      {...other value mapping...}
      default_value: {default value}
```
Example config:
```yaml
module:
  name:
    key: Module Name
    value_mapping:
      name1: name2
      default_value: empty
```

### Module Type
Format config:
```yaml
module:
  type:
    key: {json key of module type}
    value_type: {type}
    value_mapping:
      {old value}: {new value}
      {...other value mapping...}
      default_value: {default value}
```
Example config:
```yaml
module:
  type:
    key: Module Type
    value_mapping:
      type1: type2
      default_value: empty
```
### Artifacts
Format config:
```yaml
module:
  artifacts:
    key: {json key of artifacts}
    artifact:
      type: 
        key: {json key of atifact type}
        value_type: {type}
        value_mapping:
          {old value}: {new value}
          {...other value mapping...}
          default_value: {default value}
      {reqif value}:
        key: {json key of reqif value} # if not pas
        value_type: {type}
        value_mapping:
          {old value}: {new value}
          {...other value mapping...}
          default_value: {default value}
      {...other reqif value mapping...}
```
Example config:
```yaml
module:
  artifacts:
  key: List Artifact Info
  artifact:
    type:
      key: Attribute Type
      value_mapping:
        Heading: Title
        Information: Data
        MO_FUNC_REQ: MO_FUNC_REQ_new
        default_value: type
    ReqIF.ForeignID:
        key: Identifier
        value_type: number
    ReqIF.ForeignCreatedBy:
        key: Creator
    ReqIF.ForeignModifiedOn:
        key: Modified On
        value_type: date
    ReqIF.Text:
        value_type: html_string
```

#### Value type:
1. `string`
2. `number`
3. `date`
4. `html_string`

Default type is `string`

## reStructuredText Configuration

This section defines custom directives for specific artifact types.

```yaml
module:
  artifacts:
    artifact:
      __rst__:
        heading:
          atifact_type: {heading type} # map with heading type in json
          content: {content of heading} # can be a key in json or a raw string
        information:
          atifact_type: {information type} # map with information type in json
          directives:
            name: {name of directive}
            content: {}
            attributes:
              {attribute name}: {attribute value} # can be a key in json or a raw string 
              {...other attribute config...}
            directives: # subdirective config. It can be an array of directive in yaml
              - name: {name of directive}
                content: {}
                attributes:
                {attribute name}: {attribute value} # can be a key in json or a raw string
                {...other attribute config...}
              - name: {name of directive}
                content: {}
                attributes:
                {attribute name}: {attribute value} # can be a key in json or a raw string
                {...other attribute config...}
            
```

Example config: 
```yaml
module:
  artifacts:
    artifact:
      __rst__:
        heading:
          atifact_type: Title
          value: Title
        information:
          atifact_type: Data
          directives:
            name: sw_req
            attributes:
              id: Identifier
              artifact_type: Information
            html_content: ReqIF.Text
        other:
          directives:
            - name: sw_req
              attributes:
                id: Identifier
                artifact_type: Description
                crq: crq
                createdOn: Created On
              html_content: ReqIF.Text
              directives:
                - name: subdirective1
                  attributes:
                    id: Identifier
                    artifact_type: Description
                    crq: crq
                - name: subdirective2
                  attributes:
                    id: Identifier
                    artifact_type: Description
                    crq: crq
```