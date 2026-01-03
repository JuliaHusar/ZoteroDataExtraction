import unittest

from pandas.io.sql import SQLiteDatabase

from src.main import get_annotations, itemMap, get_collection_items, get_collections, instantiate_library, connect
from src.models import Tag, ItemObj, Collection, BaseLibrary

cursor: SQLiteDatabase
connection: SQLiteDatabase

if __name__ == '__main__':
    unittest.main()

class TestDataRetrieval(unittest.TestCase):
    """"
    def test_get_annotations(self):
        result_set = get_annotations()
       # annotation_map_structure: dict[int, TagObj] = {1: TagObj(1, 1, "testComment", "testText", 2, "testName")}
      #  self.assertEqual(type(get_shape(result_set)), type(get_shape(annotation_map_structure)))
    def test_get_items(self):
        result_set = get_items()
    # item_map_structure: dict[int, ItemObj] = {1: ItemObj(1, 1, "testCollection", [], {1: T})}
                if self.tag_map.tag_map_of_tagmaps.get(item_id) is None:
                continue
       """
    #Tests
    def test_collection(self):
        connect()
        test_library = BaseLibrary(1, "User")
        first_row = (get_collections(test_library).get(14))
        test_collection_object = Collection(1, "Test Collection", test_library, 1)
        self.assertIsInstance(first_row, Collection, "Not matched")


def get_shape(o):
    if isinstance(o, dict):
        return {k: get_shape(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [get_shape(o)[0]] if o else []
    else:
        return type(object)