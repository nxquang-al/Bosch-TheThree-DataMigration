# Configuration File Usage Guide

This guide provides instructions on how to use the atribute name and attribute value when migrate data from reqif to json and from json to rst.

## Reqif to Json Configuration

The module configuration section allows you to define different modules with their associated properties.

### Module Name

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

### Module Type

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

### Artifacts

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
        key: {json key of reqif value}
        value_type: {type}
        value_mapping:
          {old value}: {new value}
          {...other value mapping...}
          default_value: {default value}
      {...other reqif value mapping...}
```

#### Value type must be: string or data or number or html_string

## reStructuredText Configuration

This section defines custom directives for specific artifact types.

