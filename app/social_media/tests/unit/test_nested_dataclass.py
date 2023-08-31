from dataclasses import dataclass
from typing import List, Optional

from django.test import SimpleTestCase

from social_media.common import nested_dataclass


@dataclass
class ChildDataclass:
    id: str


@nested_dataclass
@dataclass
class ParentDataclass:
    one_child: ChildDataclass
    many_children: List[ChildDataclass]
    optional_child: Optional[ChildDataclass] = None
    many_optional_children: Optional[List[ChildDataclass]] = None

class TestNestedDataclass(SimpleTestCase):
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



