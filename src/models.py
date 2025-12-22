class TagObj:
    def __init__(self, item_id:int, tag_id:int, comment:str, text:str, parent_item_id:int, name:str):
        self.item_id  = item_id
        self.tag_id = tag_id
        self.comment = comment
        self.text = text
        self.parent_item_id = parent_item_id
        self.name = name
    def __str__(self):
        return f"Item ID: {self.item_id} TagID: {self.tag_id} ParentItem ID: {self.parent_item_id} Comment: {self.comment} Text: {self.text} Name: {self.name}"
    def determine_weight(self):

        return

class Relationship:
    def __init__(self, tag_obj_1:TagObj, tag_obj_2:TagObj):
        self.TagObj1 = tag_obj_1
        self.TagObj2 = tag_obj_2
        self.relationshipId = ""
    def __str__(self):
        return f"{self.TagObj1} {self.TagObj2}"

# The item object itself that contains annotations
class ItemObj:
    def __init__(self, collection_id:int, item_ID:int, collection_name:str, annotation_obj_list, tag_map):
        self.collection_id = collection_id
        self.itemID = item_ID
        self.annotation_obj_list = annotation_obj_list
        self.collection_name = collection_name
        self.tag_map = tag_map
    def __str__(self):
        return f"Collection: {self.collection_id} Item ID: {self.itemID} Annotation List: {self.annotation_obj_list}"

# The collection that items are held in
class CollectionObj:
    def __init__(self, collection_id: int, collection_name: str, parent_collection_ID: int, item_obj_map):
        self.collection_id = collection_id
        self.collection_name = collection_name
        self.parent_collection_ID= parent_collection_ID
        self.item_obj_map = item_obj_map
    def __str__(self):
        return f"Collection ID: {self.collection_id} Collection Name: {self.collection_name} Parent Collection ID: {self.parent_collection_ID} Item Obj List {self.item_obj_map}"
