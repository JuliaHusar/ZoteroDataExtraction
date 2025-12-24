class PrintString:
    """"""
    def __str__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

class TagObj:
    def __init__(self, tag_id, name):
        self.tag_id = tag_id
        self.name = name
    def __str__(self):
        return f"{self.tag_id} {self.name}"

class TagMap:
    def __init__(self, tag_object:TagObj):
        self.tag_object = TagObj



class AnnotationObj(PrintString):
    def __init__(self, item_id:int, comment:str, text:str, parent_item_id:int, tag_map:TagMap):
        self.item_id  = item_id
        self.comment = comment
        self.text = text
        self.parent_item_id = parent_item_id
        self.tag_map = tag_map
    # def assign_tag_map(self, ):


class Relationship:
    def __init__(self, tag_obj_1:TagObj, tag_obj_2:TagObj):
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


class CollectionObj(PrintString):
    def __init__(self, collection_id: int, collection_name: str, parent_collection_id: int):
        self.collection_id = collection_id
        self.collection_name = collection_name
        self.parent_collection_ID= parent_collection_id
        self.item_obj_map: dict[int, 'ItemObj'] = {}
    def add_item(self, item_obj_list: list['ItemObj']):
        for item in item_obj_list:
            item.collection = self
            self.item_obj_map[item.itemID] = item

class ItemObj(PrintString):
    def __init__(self, item_id:int, collection: CollectionObj, annotation_obj_list: list):
        self.itemID = item_id
        self.annotation_obj_list = annotation_obj_list
        self.collection: CollectionObj = collection
        self.collection.item_obj_map[self.itemID] = self
    @property
    def collection_name(self) -> str:
        return self.collection.collection_name

class BaseLibrary(PrintString):
    def __init__(self, library_id:int, library_type:str):
        self.library_id = library_id
        self.library_type = library_type
        self.collectionMap: dict[int, CollectionObj] = {}