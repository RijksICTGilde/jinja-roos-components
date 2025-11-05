from pprint import pprint
from scripts.generate_vscode_custom_data import create_tag_definition

class TestSelectOptions:

    def test_mapping_from_definition_to_custom_data_format(self):

        link_definition = {
            "name": "link",
            "description": "Enhanced link component with icons",
            "attributes": [
                {
                "name": "href",
                "type": "string",
                "default": "#",
                "required": False,
                "description": "Link URL"
                },
                {
                "name": "content",
                "type": "string",
                "required": False,
                "description": "Link text content"
                },
                {
                "name": "target",
                "type": "string",
                "required": False,
                "description": "Link target"
                },
                {
                "name": "icon",
                "type": "string",
                "required": False,
                "description": "Icon name"
                },
                {
                "name": "showIcon",
                "type": "enum",
                "enum_values": [
                    "no",
                    "before",
                    "after"
                ],
                "default": "no",
                "required": False,
                "description": "Icon placement"
                },
                {
                "name": "iconSize",
                "type": "enum",
                "enum_values": [
                    "xs",
                    "sm",
                    "md",
                    "lg"
                ],
                "default": "sm",
                "required": False,
                "description": "Icon size"
                },
                {
                "name": "iconColor",
                "type": "string",
                "required": False,
                "description": "Icon color"
                },
                {
                "name": "noUnderline",
                "type": "boolean",
                "default": False,
                "required": False,
                "description": "Remove underline"
                },
                {
                "name": "color",
                "type": "string",
                "required": False,
                "description": "Link color"
                },
                {
                "name": "weight",
                "type": "string",
                "required": False,
                "description": "Font weight"
                },
                {
                "name": "fullContainer",
                "type": "boolean",
                "default": False,
                "required": False,
                "description": "Full container link"
                },
                {
                "name": "class",
                "type": "string",
                "required": False,
                "description": "Additional CSS classes"
                }
            ],
            "slots": [],
            "examples": [
                "<c-link href=\"/page\" content=\"Link Text\" showIcon=\"after\" icon=\"arrow-right\" />"
            ],
            "allow_preview": True,
            "requires_children": False,
            "preview_example": None
            }

        custom_data_format = create_tag_definition(link_definition['name'], link_definition)

        expected = {
            'name': 'c-link',
            'description': 'Enhanced link component with icons',
            'attributes': [
                {
                    'name': 'href',
                    'description': 'Link URL (default: `#`)'
                },
                {
                    'name': 'content',
                    'description': 'Link text content'
                },
                {
                    'name': 'target',
                    'description': 'Link target'
                },
                {
                    'name': 'icon',
                    'description': 'Icon name'
                },
                {
                    'name': 'showIcon',
                    'description': 'Icon placement (default: `no`)',
                    'values': [
                        {'name': 'no'},
                        {'name': 'before'},
                        {'name': 'after'}
                    ]
                },
                {
                    'name': 'iconSize',
                    'description': 'Icon size (default: `sm`)',
                    'values': [
                        {'name': 'xs'},
                        {'name': 'sm'},
                        {'name': 'md'},
                        {'name': 'lg'}
                    ]
                },
                {
                    'name': 'iconColor',
                    'description': 'Icon color'
                },
                {
                    'name': 'noUnderline',
                    'description': 'Remove underline (default: `false`)',
                    'values': [
                        {'name': 'true'},
                        {'name': 'false'}
                    ]
                },
                {
                    'name': 'color',
                    'description': 'Link color'
                },
                {
                    'name': 'weight',
                    'description': 'Font weight'
                },
                {
                    'name': 'fullContainer',
                    'description': 'Full container link (default: `false`)',
                    'values': [
                        {'name': 'true'},
                        {'name': 'false'}
                    ]
                },
                {
                    'name': 'class',
                    'description': 'Additional CSS classes'
                }
            ]
        }

        assert custom_data_format == expected
