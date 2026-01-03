from __future__ import annotations
from typing import NamedTuple

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


class AnnotationKey(NamedTuple):
    item_id: int
    parent_item_id: int

class TagKey(NamedTuple):
    item_id: int
    tag_id: int



class TagMap(PrintString):
    def __init__(self):
        self.tag_map_of_tagmaps: dict[int, dict[int, Tag]] = {}
        # Remember that it's sorted by ASC id already from SQL DB
    def populate_parent_item_tag_map(self, tag_parent_id: int):
        self.tag_map_of_tagmaps[tag_parent_id] = {}
        return
    def populate_individual_tags(self, individual_tag: Tag, current_parent_id: int):
        self.tag_map_of_tagmaps[current_parent_id][individual_tag.tag_id] = individual_tag
        return

    def process_raw_tuples(self, raw_tag_list: list[tuple]):
        item_id_counter: int = 0
        for item in raw_tag_list:
            tag_id, item_id, tag_type, name = item
            individual_tag = Tag(tag_id, name, tag_type, item_id)
            if item_id != item_id_counter:
                self.populate_parent_item_tag_map(item_id)
                item_id_counter = item_id
            self.populate_individual_tags(individual_tag, item_id_counter)
        return self.tag_map_of_tagmaps

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


class FieldMap(PrintString):
    def __init__(self):
        self.field_map: dict[int, dict[int, Field]] = {}
        # 1-Many Data relationship/Mapping with all the CollectionID -> {FieldItem1, FieldItem2...}
    def create_field_map(self, field_list: list[tuple]):
        field_map: dict[int, dict[int, Field]] = {}
        item_counter: int = 0
        for field_item in field_list:
            item_id, field_id, value_id, value, field_name = field_item
            if item_id != item_counter:
                self.field_map[item_id] = {}
                item_counter = item_id
            self.field_map[item_id][field_id] = Field(item_id, field_id, field_name, value_id, value)
        return field_map
    #Function checks if field maps and item maps are equal in the keys that they have. If they aren't then
    # a new key is created in the respective list. This prevents the key-error where the compiler doesn't find a necessary key
    def crosscheck_maps(self, collection_item_id_list):
        """:arg: collection_item_id_list"""
        unpaired_maps = []
        for item_id in collection_item_id_list:
            if item_id in self.field_map:
                continue
            else:
             #   print(item_id)
                unpaired_maps.append(item_id)
       # print(unpaired_maps.__sizeof__())


class Field(PrintString):
    """:arg value of field is determined by the tuple [itemID,valueID]"""
    def __init__(self, item_id:int, field_id:int, field_name:str, value_id:int,value:str):
        self.item_id = item_id
        self.field_id = field_id
        self.field_name = field_name
        self.value_id = value_id
        self.value = value


class Collection(PrintString):
    def __init__(self, collection_id: int, collection_name: str, parent_collection_id: int):
        self.collection_id = collection_id
        self.collection_name = collection_name
        self.parent_collection_ID= parent_collection_id
        self.item_obj_map: dict[int, 'CollectionItem'] = {}
        self.floating_items: dict[int, 'Attachment'] = {}
    def add_parent_item_obj(self, collection_item: tuple, tag_map:dict[int, Tag], field_map: FieldMap):
        collection_id, item_id, collection_name, item_type_id, date_added, date_modified, parent_item_id, link_mode, path, content_type = collection_item
        if item_id not in field_map.field_map:
            print("none")
        field_map_item_dict = field_map.field_map[item_id]
            # Create key if it doesn't already exist
        collection_item = CollectionItem(item_id, tag_map, item_type_id, date_added, date_modified, field_map_item_dict, [])
        self.item_obj_map[collection_item.itemID] = collection_item

class ItemObj(PrintString):
    def __init__(self, item_id:int, tag_map:dict[int, Tag], item_type_id:int, date_added:str, date_modified:str):
        self.itemID = item_id
        self.tag_map = tag_map
        self.item_type_id = item_type_id
        self.date_added = date_added
        self.date_modified = date_modified


"""class NoteObj(PrintString):
    def __init__(self):"""

class CollectionItem(ItemObj, PrintString):
    """Collection Item differs from regular item by including field_map_obj and attachment_list"""
    def __init__(self, item_id:int, tag_map:dict[int, Tag], item_type_id:int, date_added:str, date_modified:str, field_map_obj:dict[int, Field], attachment_list:list['Attachment']):
        super().__init__(item_id, tag_map, item_type_id, date_added, date_modified)
        self.field_map_obj = field_map_obj
        self.attachment_list = attachment_list

# Attachments in my dataset didn't have tags, but I suppose that other datasets do use them, as such they inherit from ItemObj
class Attachment(ItemObj, PrintString):
    def __init__(self, item_id:int, tag_map:dict[int, Tag], item_type_id:int, date_added:str, date_modified:str, link_mode:int, path:str, content_type:str, parent_item_id:int, field_map_obj:dict[int, Field]):
        super().__init__(item_id, tag_map, item_type_id, date_added, date_modified)
        self.link_mode = link_mode
        self.path = path
        self.content_type = content_type
        self.parent_item_id = parent_item_id
        self.field_map = field_map_obj

class Annotation(ItemObj, PrintString):
    """Annotation Object is a type of item object, complete with its own unique itemID and list of tags.
    As such, annotationObj inherits from ItemObj"""
    def __init__(self, item_id:int, tag_map:dict[int, Tag], item_type_id:int, date_added:str, date_modified:str, comment:str, text:str, parent_item_id:int):
        super().__init__(item_id, tag_map, item_type_id, date_added, date_modified)
        self.comment = comment
        self.text = text
        self.parent_item_id = parent_item_id
    # def assign_tag_map(self, ):

class AnnotationMap(PrintString):
    def __init__(self, tag_map:TagMap):
        self.annotation_map: dict[AnnotationKey, Annotation] = {}
        self.tag_map = tag_map
    def process_raw_tuples(self, raw_annotation_list: list[tuple]):
        for item in raw_annotation_list:
            item_id, parent_item_id, text, comment, color, item_type_id, date_added, client_date_modified = item
            key = AnnotationKey(item_id=item_id, parent_item_id=parent_item_id)
            # TAGS ARE STORED IN SUBCOLLECTION OF ITEMID SO THAT WE CAN ACCESS THE ITEM ID ITSELF
            self.annotation_map[key] = Annotation(item_id, self.get_sub_tag_map(item_id), item_type_id, date_added, client_date_modified, comment, text, parent_item_id)
    def get_sub_tag_map(self, parent_id):
        if self.tag_map.tag_map_of_tagmaps.get(parent_id) is None:
            return TagMap()
        else:
            return self.tag_map.tag_map_of_tagmaps.get(parent_id)

class BaseLibrary:
    """:arg
    library_id:int The library that collections are contained in
    library_type:str Whether the library is single user or group
    """
    def __init__(self, library_id:int, library_type:str):
        self.library_id = library_id
        self.library_type = library_type
        self.collectionMap: dict[int, Collection] = {}
    def add_collection(self, raw_collection_list: list[tuple]):
        raw_collection_list.insert(0, (0, 'BaseCollection', None))
        for collection_item in raw_collection_list:
            collection_id, collection_name, parent_id = collection_item
            collection_item = Collection(collection_id, collection_name, parent_id)
            self.collectionMap[collection_item.collection_id] = collection_item
    def populate_collections(self, raw_item_list: list[tuple], tag_map: TagMap, field_map: FieldMap):
        current_parent_collection_id = 0
        #Note to self: Lookout for unintended recursion when creating these dicts
        prev_id = 0
        for item in raw_item_list:
            collection_id, item_id, collection_name, item_type_id, date_added, date_modified, parent_item_id, link_mode, path, content_type = item
            current_tag_map =  tag_map.tag_map_of_tagmaps.get(parent_item_id)
            if item_type_id == (3 or 28):
                attachment_obj = Attachment(item_id, current_tag_map, item_type_id, date_added, date_modified, link_mode, path, content_type, parent_item_id, field_map.field_map.get(item_id))
                if parent_item_id is not None: #If item is attachment object that is a part of an existing parent-item and not just free-floating
                    print(self.collectionMap.get(current_parent_collection_id).item_obj_map)
                    self.collectionMap.get(current_parent_collection_id).item_obj_map.get(prev_id).attachment_list.append(attachment_obj)
                else:
                    self.collectionMap.get(0).floating_items[item_id] = attachment_obj
            else:
                if collection_id is not None:
                    self.collectionMap.get(collection_id).add_parent_item_obj(item, current_tag_map, field_map)
                    current_parent_collection_id = collection_id
                else:
                    self.collectionMap.get(0).add_parent_item_obj(item, current_tag_map, field_map)
                    current_parent_collection_id = 0
                print("iterated")
                prev_id = item_id
            #Attachments have fields so we'll have to figure out a way of getting all of these into collection items
            """
        for key, collection_object_value in self.collectionMap.items():
            collection_object_value.add_item_obj()
            """





