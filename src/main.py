import sqlite3
import logging
from inspect import stack
from typing import Tuple

from pandas.io.sql import SQLiteDatabase

from src.models import ItemObj, Annotation, BaseLibrary, TagMap, AnnotationMap, FieldMap

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
                        "FROM itemAnnotations INNER JOIN items ON itemAnnotations.itemID == items.itemID "
                        "ORDER BY itemAnnotations.parentItemID ASC")
    cursor_execute = cursor.execute(annotation_query)
    annotation_list = cursor_execute.fetchall()
    annotation_map = AnnotationMap(tag_map)
    annotation_map.process_raw_tuples(annotation_list)
    return annotation_map

def get_tags():
    """:returns map of tags, their names, types, and relevant ID's: Dict[TagID:[ItemID, type, name]]
    Many-Many Relationship in relation to item entities"""
    query = ("SELECT itemTags.tagID, itemTags.itemID, itemTags.type, tags.name "
             "FROM itemTags INNER JOIN tags ON tags.tagID = itemTags.tagID ORDER BY itemTags.itemID ASC")
    cursor_execute = cursor.execute(query)
    raw_tag_list = cursor_execute.fetchall()
    tag_map_obj:TagMap = TagMap()
    tag_map_obj.process_raw_tuples(raw_tag_list)
    return tag_map_obj

def get_collection_items(library: BaseLibrary, raw_collection_list: list[tuple], tag_map:TagMap, field_map:FieldMap):
    """:returns list of collectionItems. The way that Zotero is structured, literally EVERYTHING is an item,
    including annotations (and annotations are related to collection items)"""
    # Select all items, and then full join so that if an item has multiple attachments, these attachments and items will have their own rows.
    # There will be no primary key, but rather a foreign key that combines the itemID and parentItemID
    item_query = (
        # Select all parent items and their respective children items. The tricky thing with this is that collectionItems exclude anything out of a collection,
        # so anything that's in a base library would be ignored. As such this query will select ALL items minus annotation and notes (those are dealt with separately'
        "SELECT collectionItems.collectionID, items.itemID, collections.collectionName, items.itemTypeID, items.dateAdded, items.clientDateModified, itemAttachments.parentItemID, itemAttachments.linkMode, itemAttachments.path, itemAttachments.contentType "
        "FROM items FULL JOIN collectionItems ON collectionItems.itemID = items.itemID "
        "FULL JOIN itemAttachments ON itemAttachments.itemID = items.itemID "
        "FULL JOIN collections ON collectionItems.collectionID = collections.collectionID "
        "WHERE ((items.libraryID == ?) "
        "AND (items.itemTypeID NOT IN (1, 28))) "
        "ORDER BY items.itemId ASC "
    )

    # Query selects all distinct collectionIDs, from items that belong to a collection. This way annotations are ignored.
    item_id_query = ("SELECT DISTINCT collectionItems.itemID FROM collectionItems "
                     "INNER JOIN collections on collectionItems.collectionID = collections.collectionID "
                     "WHERE collections.libraryID == ? "
                     "ORDER BY itemID ASC ")
    # Add error handling for the list retrieval and then subsequent handling
    cursor_execute = (cursor.execute(item_query, (library.library_id,)))
    collection_item_list = cursor_execute.fetchall()
    cursor_execute = (cursor.execute(item_id_query, (library.library_id,)))
    collection_id_list = cursor_execute.fetchall()
    # Check to make sure that all field values are accounted for
    field_map.crosscheck_maps(collection_item_id_list=collection_id_list)
    library.add_collection(raw_collection_list=raw_collection_list)
    library.populate_collections(raw_item_list=collection_item_list, tag_map=tag_map, field_map=field_map)
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
        "FROM itemData LEFT JOIN fields ON itemData.fieldID = fields.fieldID "
        "LEFT JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID "
        "ORDER BY itemID ASC"
    )
    cursor_execute = cursor.execute(field_query)
    field_list = cursor_execute.fetchall()
    field_map:FieldMap = FieldMap()
    field_map.create_field_map(field_list)
    return field_map

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
    field_map = get_field_items()
    tag_map = get_tags()
    get_annotations(tag_map)
    library = instantiate_library()
    get_all_items(library)
    collection_list = get_collections(library=library)
    get_collection_items(library=library, raw_collection_list=collection_list, tag_map=tag_map, field_map=field_map)

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