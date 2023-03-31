from schematics.types import ModelType, StringType, PolyModelType, DictType
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, ListDynamicLayout, \
    TableDynamicLayout
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, EnumDyField, MoreField
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta
from spaceone.inventory.model.recommender.recommendation.recommender_data import Recommender

recommender_details = ItemDynamicLayout.set_fields('Recommender Details', fields=[
    TextDyField.data_source('Name', 'data.name'),
    TextDyField.data_source('ID', 'data.id'),
    TextDyField.data_source('Description', 'data.description'),
    EnumDyField.data_source('State', 'data.state', default_state={
        'safe': ['OK'],
        'disable': ['Error'],
        'alert': ['Warning'],
    }),
    TextDyField.data_source('Resource Count', 'data.resource_count'),
    TextDyField.data_source('Cost Savings', 'data.cost_savings'),
    EnumDyField.data_source('Priority Level', 'data.display.priority_display', default_badge={
        'red.500': ['Highest'],
        'coral.500': ['Second Highest'],
        'yellow.300': ['Second Lowest'],
        'gray.500': ['Lowest'],
        'black': ['Unspecified']
    })
])

detail_meta = ListDynamicLayout.set_layouts('Details',
                                            layouts=[recommender_details])

detail_recommendations_meta = TableDynamicLayout.set_fields(
    'Recommendations',
    root_path='data.recommendations',
    fields=[
        MoreField.data_source('Description', 'description',
                              options={
                                  'layout': {
                                      'name': 'Insights',
                                      'options': {
                                          'type': 'popup',
                                          'layout': {
                                              'type': 'simple-table',
                                              'options': {
                                                  'root_path': 'insights',
                                                  'fields': [
                                                      {
                                                          "type": "text",
                                                          "key": "description",
                                                          "name": "Description"
                                                      },
                                                      {
                                                          "type": "enum",
                                                          "key": "severity",
                                                          "name": "Severity",
                                                          "options": {
                                                              "items": {
                                                                  "CRITICAL": {
                                                                      "name": "CRITICAL",
                                                                      "type": "state",
                                                                      "options": {
                                                                          "icon": {
                                                                              "color": "red.500"
                                                                          }
                                                                      }
                                                                  },
                                                                  "HIGH": {
                                                                      "name": "HIGH",
                                                                      "type": "state",
                                                                      "options": {
                                                                          "icon": {
                                                                              "color": "red.500"
                                                                          }
                                                                      }
                                                                  },
                                                                  "SEVERITY_UNSPECIFIED": {
                                                                      "name": "SEVERITY_UNSPECIFIED",
                                                                      "type": "state",
                                                                      "options": {
                                                                          "icon": {
                                                                              "color": "red.500"
                                                                          }
                                                                      }
                                                                  },
                                                                  "MEDIUM": {
                                                                      "name": "MEDIUM",
                                                                      "type": "state",
                                                                      "options": {
                                                                          "icon": {
                                                                              "color": "gray.500"
                                                                          }
                                                                      }
                                                                  },
                                                                  "LOW": {
                                                                      "name": "LOW",
                                                                      "type": "state",
                                                                      "options": {
                                                                          "icon": {
                                                                              "color": "gray.500"
                                                                          }
                                                                      }
                                                                  }
                                                              }
                                                          }
                                                      },
                                                      {
                                                          "type": "enum",
                                                          "key": "category",
                                                          "name": "Category",
                                                          "options": {
                                                              "items": {
                                                                  "COST": {
                                                                      "type": "badge",
                                                                      "options": {
                                                                          "background_color": "indigo.500"
                                                                      }
                                                                  },
                                                                  "SUSTAINABILITY": {
                                                                      "type": "badge",
                                                                      "options": {
                                                                          "background_color": "peacock.500"
                                                                      }
                                                                  },
                                                                  "RELIABILITY": {
                                                                      "type": "badge",
                                                                      "options": {
                                                                          "background_color": "violet.500"
                                                                      }
                                                                  },
                                                                  "PERFORMANCE": {
                                                                      "type": "badge",
                                                                      "options": {
                                                                          "background_color": "blue.500"
                                                                      }
                                                                  },
                                                                  "MANAGEABILITY": {
                                                                      "type": "badge",
                                                                      "options": {
                                                                          "background_color": "green.500"
                                                                      }
                                                                  },
                                                                  "SECURITY": {
                                                                      "type": "badge",
                                                                      "options": {
                                                                          "background_color": "yellow.500"
                                                                      }
                                                                  },
                                                                  "CATEGORY_UNSPECIFIED": {
                                                                      "type": "badge",
                                                                      "options": {
                                                                          "background_color": "coral.500"
                                                                      }
                                                                  }
                                                              }
                                                          }
                                                      }
                                                  ]
                                              }
                                          }
                                      }
                                  }
                              }),
        EnumDyField.data_source('State', 'state', default_state={
            'safe': ['ACTIVE'],
            'disable': ['ACCEPTED'],
            'alert': ['STATE_UNSPECIFIED', 'DISMISSED'],
        }),
        TextDyField.data_source('Cost Savings', 'cost_savings'),
        TextDyField.data_source('Affected Resource', 'affected_resource', reference={
            'resource_type': 'inventory.CloudService',
            'reference_key': 'name'
        }),
        TextDyField.data_source('Location', 'location'),
        EnumDyField.data_source('Priority Level',
                                'priority_level',
                                default_badge={
                                    'red.500': ['Highest'],
                                    'coral.500': ['Second Highest'],
                                    'yellow.300': ['Second Lowest'],
                                    'gray.500': ['Lowest'],
                                    'black': ['Unspecified']
                                }),
        TextDyField.data_source('Operations', 'operations')
    ])

recommendations_meta = ListDynamicLayout.set_layouts('Recommendations',
                                                     layouts=[detail_recommendations_meta])
recommendation_meta = CloudServiceMeta.set_layouts([detail_meta, recommendations_meta])


class RecommenderResource(CloudServiceResource):
    tags = DictType(StringType, serialize_when_none=False)
    cloud_service_group = StringType(default='Recommender')


class RecommendationResource(RecommenderResource):
    cloud_service_type = StringType(default='Recommendation')
    data = ModelType(Recommender)
    _metadata = ModelType(CloudServiceMeta, default=recommendation_meta, serialized_name='metadata')


class RecommendationResponse(CloudServiceResponse):
    resource = PolyModelType(RecommendationResource)
