from enum import Enum
from typing import Tuple

class_registry = {}

class PrintString:
    def __repr__(self):
        # vars(self) returns a dictionary of all attributes
        attributes = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{self.__class__.__name__}({attributes})"


class Tag(PrintString):
    def __init__(self, tag_id:int, name:str, tag_type:int, item_id: int):
        self.tag_id = tag_id
        self.name = name
        self.tag_type = tag_type
        self.item_id = item_id

class TagMap(PrintString):
    def __init__(self):
        self.tag_map: dict[Tuple[int, int], Tag] = {}
    def process_raw_tuples(self, raw_tag_list: list[tuple]):
        for item in raw_tag_list:
            tag_id, item_id, tag_type, name = item
            self.tag_map[(item_id, tag_id)] = Tag(tag_id, name, tag_type, item_id)


class Relationship:
    def __init__(self, tag_obj_1:Tag, tag_obj_2:Tag):
        self.TagObj1 = tag_obj_1
        self.TagObj2 = tag_obj_2
        self.relationshipId = ""
    def __str__(self):
        return f"{self.TagObj1} {self.TagObj2}"

# The collection that items are held in
"""I could do one of two approaches here. I could either create classes for collections and items
 and then list all of their subclasses as items in a list or a map. This would make sense programmatically,
 could be instantiated in the main script at initialization, keeps the code for adding new items organized,
but might be tricky to understand. The other approach is a more top-down approach that involves creating
individual maps. I've already tried that, so it might be worth it to try the first approach."""



class Collection(PrintString):
    def __init__(self, collection_id: int, collection_name: str, parent_collection_id: int):
        self.collection_id = collection_id
        self.collection_name = collection_name
        self.parent_collection_ID= parent_collection_id
        self.item_obj_map: dict[int, 'ItemObj'] = {}
    def add_item_obj(self, item: tuple):
            collection_id, item_id, collection_name = item
            item = ItemObj(item_id, [])
            item.collection = self
            self.item_obj_map[item.itemID] = item

class ItemObj(PrintString):
    def __init__(self, item_id:int, tag_map:dict[int, Tag], item_type_id:int, date_added:str, date_modified:str):
        self.itemID = item_id
        self.tag_map = tag_map
        self.item_type_id = item_type_id
        self.date_added = date_added
        self.date_modified = date_modified
    @property
    def collection_name(self) -> str:
        return self.collection_name

class Field:
    """:arg value of field is determined by the tuple [itemID,valueID]"""
    def __init__(self, item_id:int, field_id:int, field_name:str, value_id:int,value:str):
        self.item_id = item_id
        self.field_id = field_id
        self.field_name = field_name
        self.value_id = value_id
        self.value = value


"""class NoteObj(PrintString):
    def __init__(self):"""

class CollectionItem(ItemObj, PrintString):
    def __init__(self, item_id:int, tag_map:dict[int, Tag], item_type_id:int, date_added:str, date_modified:str, field_obj:Field):
        super().__init__(item_id, tag_map, item_type_id, date_added, date_modified)
        self.field_obj = field_obj


class Annotation:
    """Annotation Object is a type of item object, complete with its own unique itemID and list of tags.
    As such, annotationObj inherits from ItemObj"""
    def __init__(self, item_id:int, tag_map:TagMap, item_type_id:int, date_added:str, date_modified:str, comment:str, text:str, parent_item_id:int,):
        super().__init__(item_id,tag_map,item_type_id,date_added,date_modified)
        self.comment = comment
        self.text = text
        self.parent_item_id = parent_item_id
    # def assign_tag_map(self, ):

class BaseLibrary:
    """:arg
    library_id:int The library that collections are contained in
    library_type:str Whether the library is single user or group """
    def __init__(self, library_id:int, library_type:str):
        self.library_id = library_id
        self.library_type = library_type
        self.collectionMap: dict[int, Collection] = {}
    def add_collection(self, raw_collection_list: list[tuple]):
        for collection_item in raw_collection_list:
            collection_id, collection_name, parent_id = collection_item
            collection_item = Collection(collection_id, collection_name, parent_id)
            self.collectionMap[collection_item.collection_id] = collection_item
    def populate_collections(self, raw_item_list: list[tuple]):
        for item in raw_item_list:
            collection_id, item_id, collection_name = item
            self.collectionMap.get(collection_id).add_item_obj(item)
        for key, collection_object_value in self.collectionMap.items():
            collection_object_value.add_item_obj()



