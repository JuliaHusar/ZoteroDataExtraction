import unittest

from src.main import get_annotations, itemMap, annotation_map, get_items
from src.models import TagObj, ItemObj

if __name__ == '__main__':
    unittest.main()

class TestDataRetrieval(unittest.TestCase):
    def test_get_annotations(self):
        result_set = get_annotations()
        annotation_map_structure: dict[int, TagObj] = {1: TagObj(1, 1, "testComment", "testText", 2, "testName")}
        self.assertEqual(type(get_shape(result_set)), type(get_shape(annotation_map_structure)))
    def test_get_items(self):
        result_set = get_items()
        item_map_structure: dict[int, ItemObj] = {1: ItemObj(1, 1, "testCollection", [], {1: T})}

def get_shape(o):
    if isinstance(o, dict):
        return {k: get_shape(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [get_shape(o)[0]] if o else []
    else:
        return type(object)