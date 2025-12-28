import sqlite3
import logging
from inspect import stack
from typing import Tuple

from pandas.io.sql import SQLiteDatabase

from src.models import ItemObj, Annotation, BaseLibrary, TagMap, AnnotationMap

# Initial connection, for now it's directory, but ideally we want users to be able to make a copy of this.... just in case
logger = logging.getLogger(__name__)
file_path = "zotero.sqlite"

#Define global vars
cursor: SQLiteDatabase
connection: SQLiteDatabase

itemMap: dict[int, ItemObj] = {}
relationshipList = []
noIdCount: int = 0


def connect():
    global connection
    global cursor
    try:
        connection = sqlite3.connect(f"file:{file_path}?mode=rw", uri=True)
        cursor = connection.cursor()
    except Exception as e:
        print(f"Database Connection failed: {e}. Check to see if the zotero.sqlite file is located in the root directory, and it is spelled exactly as <zotero.sqlite>, or whatever value you have in file_path")
        raise Exception


def instantiate_library():
    library_query = "SELECT libraries.libraryID, libraries.type FROM libraries"
    library_list = (cursor.execute(library_query)).fetchall()
    # Return however many base libraries you need. For example if you're doing 4 libraries, return a list of four base collections
    return BaseLibrary(library_list[0][0], library_list[0][1])

def get_annotations(tag_map: TagMap):
    """:returns annotation_map of annotations and tags within these annotations
    :type tag_map
    The parent id relates the item to a central node or 'item'.
    1-Many relationship"""
    global noIdCount
    annotation_query = ("SELECT itemAnnotations.itemID, itemAnnotations.parentItemID, "
                        "itemAnnotations.text, itemAnnotations.comment, itemAnnotations.color, "
                        "items.itemTypeID, items.dateAdded, items.clientDateModified "
                        "FROM itemAnnotations INNER JOIN items ON itemAnnotations.itemID == items.itemID")
    cursor_execute = cursor.execute(annotation_query)
    annotation_list = cursor_execute.fetchall()
    annotation_map = AnnotationMap(tag_map)
    annotation_map.process_raw_tuples(annotation_list)
    #TODO: Ok so, instantiate these annotation items, and then create a map where the key is a
    # tuple of the individual itemID and the parentItemID. THEN, write a function that merges this annotation map with the other map of collection objects,
    # so that the collectionItems are the parents and the annotation objects are the children.
    # TODO: The collection map (general collection NOT the item, these are two different classes)
    #  will have to contain all annotation items and collection items. The map of collection/annotation Items will have to be passed into this
    #  larger list of collections BASED ON THE KEY OF THE COLLECTION ITEMS. THIS IS CRUCIAL. the key of the annotation ids is only useful
    #  insofar as we're trying to get them into the actual collectionItem maps. Once they're in the maps then the collectionItem id from the
    #  collectionItems table can be used to figure out the parentCollectionID. Because the tags are contained within the annotation map and the
    #  collectionItem map, we don't have to worry about that. I think this will work.
    """
    try:
        #Needs to be tagID
        parent_key: int = annotation_item[2]
        tag_id: int = annotation_item[0]
        annotation_map[(parent_key, tag_id)] = Annotation(parent_key, annotation_item[0], annotation_item[6], annotation_item[5], annotation_item[4], annotation_item[1])
    except (RuntimeError, TypeError, NameError):
        # If for whatever reason there isn't a parent key
        parent_key = noIdCount
        annotation_map[parent_key] = Annotation(annotation_item[2], annotation_item[0], annotation_item[6], annotation_item[5], annotation_item[4], annotation_item[1])
        noIdCount = + 1
        """
    return annotation_map

def get_tags():
    """:returns map of tags, their names, types, and relevant ID's: Dict[TagID:[ItemID, type, name]]
    Many-Many Relationship in relation to item entities"""
    query = ("SELECT itemTags.tagID, itemTags.itemID, itemTags.type, tags.name "
             "FROM itemTags INNER JOIN tags ON tags.tagID = itemTags.tagID ORDER BY itemTags.itemID ASC")
    cursor_execute = cursor.execute(query)
    raw_tag_list = cursor_execute.fetchall()
    tag_map_obj = TagMap()
    tag_map_obj.process_raw_tuples(raw_tag_list)
    return tag_map_obj


def get_collection_items(library: BaseLibrary, raw_collection_list: list[tuple]):
    """:returns list of collectionItems. The way that Zotero is structured, literally EVERYTHING is an item,
    including annotations (and annotations are related to collection items)"""
    item_query = (
        # Parent collection id is not needed for items, because items will be contained with collection map
        "SELECT collectionItems.collectionID, collectionItems.itemID, collections.collectionName"
        " FROM collections FULL JOIN collectionItems ON collections.collectionID = collectionItems.collectionID"
        " WHERE collections.libraryID == ?")
    # Add error handling for the list retrieval and then subsequent handling
    cursor_execute = (cursor.execute(item_query, (library.library_id,)))
    collection_item_list = cursor_execute.fetchall()

    library.add_collection(raw_collection_list)
    library.populate_collections(collection_item_list)
    return

def get_all_items(library: BaseLibrary):
    item_query = (
        "SELECT items.itemID, items.itemTypeID, items.dateAdded, items.clientDateModified "
        "FROM items WHERE items.libraryID == ?")
    cursor_execute = (cursor.execute(item_query,(library.library_id,)))
    item_list = cursor_execute.fetchall()
    return


def get_field_items():
    field_query = (
        "SELECT itemData.itemID, itemData.fieldID, itemData.valueID, itemDataValues.value, fields.fieldName "
        "FROM itemData LEFT JOIN fields ON itemData.fieldID = fields.fieldID"
        " LEFT JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID"
    )
    cursor_execute = cursor.execute(field_query)
    item_list = cursor_execute.fetchall()
    return item_list

def get_collections(library: BaseLibrary):
    """:returns a list of all collections
    library ID can be range from 1 to n, depending on how what library the user wants to draw from (most users will have 1)
    Future update should allow to combine all libraries using relational algebra or smth
    """
    collection_query = ("SELECT collections.collectionID, collections.collectionName, collections.parentCollectionID "
        " FROM collections WHERE collections.libraryID == ?")
    cursor_execute = (cursor.execute(collection_query, (library.library_id,)))
    # Add error handling here if it can't fetch everything so the returned collection is empty
    collection_list = cursor_execute.fetchall()
    return collection_list

def main():
    # Define Vars
    """Algorithm: Bottom-up Approach
    1. Retrieve every single tag and its attributes (name, type) and map the
    tag object to an itemID + TagID TUPLE (this itemID can be a publishedItemObj or an annotationObj) (DONE)
    2. Retrieve all collectionItems and itemAnnotations and instantiate them with the itemID serving as a key
    3. Insert all items into

    """
    library: BaseLibrary

    connect()
    tag_map = get_tags()
    get_annotations(tag_map)
    library = instantiate_library()
    get_all_items(library)
    collection_list = get_collections(library)
    get_collection_items(library, collection_list)

    """
    If parentCollectionID === None
        parentCollectionID = 'main'
    """

"""for i, collectionItem in enumerate(collectionMap.values()):
    for itemObj in
    collectionItem.item_obj_map +="""


#### e.g.
""""
commentObject: {itemID: Int, comment: String, tags:[{itemID:int, tagID:int, tag: string }], text: String, highlightColor: String} 
(itemID + tagID are unique identifier for tag placement bcs combined acts as a key, while itemID serves as a key for commentObject itself)
{
tagWeight:int,
  listOfParentItems:[
        itemObjects {
            
  }]
}
"""

if __name__ == "__main__":
    main()