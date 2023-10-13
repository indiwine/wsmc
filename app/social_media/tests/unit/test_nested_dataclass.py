from dataclasses import dataclass
from typing import List, Optional

from django.test import SimpleTestCase

from social_media.common import nested_dataclass


@nested_dataclass
class ChildDataclass:
    id: str

@nested_dataclass
class BaseChild:
    base_id: str

@nested_dataclass
class ExtendedChild(BaseChild):
    extended_id: str

@nested_dataclass
class ParentDataclass:
    one_child: ChildDataclass
    many_children: List[ChildDataclass]
    optional_child: Optional[ChildDataclass] = None
    many_optional_children: Optional[List[ChildDataclass]] = None
    missing_list_type: Optional[List] = None
    extended_child: Optional[ExtendedChild] = None




class TestNestedDataclass(SimpleTestCase):

    def test_extended_child(self):
        parent = ParentDataclass(
            one_child={'id': '1'},
            many_children=[],
            extended_child={'base_id': '2', 'extended_id': '3'},
        )

        self.assertIsInstance(parent.extended_child, ExtendedChild)
        self.assertIsInstance(parent.extended_child, BaseChild)

    def test_one_to_one(self):
        parent = ParentDataclass(
            one_child={'id': '1'},
            many_children=[],
        )

        self.assertIsInstance(parent.one_child, ChildDataclass)

    def test_many_children(self):
        parent = ParentDataclass(
            one_child={'id': '1'},
            many_children=[{'id': '2'}, {'id': '3'}],
        )

        self.assertIsInstance(parent.many_children[0], ChildDataclass)
        self.assertIsInstance(parent.many_children[1], ChildDataclass)


    def test_already_dataclass(self):
        parent = ParentDataclass(
            one_child=ChildDataclass(id='1'),
            many_children=[ChildDataclass(id='2'), ChildDataclass(id='3')],
        )

        self.assertIsInstance(parent.one_child, ChildDataclass)
        self.assertIsInstance(parent.many_children[0], ChildDataclass)
        self.assertIsInstance(parent.many_children[1], ChildDataclass)

    def test_optional_child(self):
        parent = ParentDataclass(
            one_child={'id': '1'},
            many_children=[{'id': '2'}, {'id': '3'}],
            optional_child={'id': '4'},
        )

        self.assertIsInstance(parent.optional_child, ChildDataclass)

    def test_many_optional_children(self):
        parent = ParentDataclass(
            one_child={'id': '1'},
            many_children=[{'id': '2'}, {'id': '3'}],
            optional_child={'id': '4'},
            many_optional_children=[{'id': '5'}, {'id': '6'}],
        )

        self.assertIsInstance(parent.many_optional_children[0], ChildDataclass)
        self.assertIsInstance(parent.many_optional_children[1], ChildDataclass)

    def test_missing_list_type(self):
        parent = ParentDataclass(
            one_child={'id': '1'},
            many_children=[{'id': '2'}, {'id': '3'}],
            optional_child={'id': '4'},
            many_optional_children=[{'id': '5'}, {'id': '6'}],
            missing_list_type=[],
        )

        self.assertIsInstance(parent.missing_list_type, list)


    def test_unknown_field(self):
        parent = ParentDataclass(
            one_child={'id': '1'},
            many_children=[{'id': '2'}, {'id': '3'}],
            optional_child={'id': '4'},
            many_optional_children=[{'id': '5'}, {'id': '6'}],
            missing_list_type=[],
            unknown_field='unknown',
        )

        self.assertFalse(hasattr(parent, 'unknown_field'))

