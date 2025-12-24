import sqlite3
import logging
from typing import Tuple

from pandas.io.sql import SQLiteDatabase

from src.models import CollectionObj, ItemObj, AnnotationObj, BaseLibrary

# Initial connection, for now it's directory, but ideally we want users to be able to make a copy of this.... just in case
logger = logging.getLogger(__name__)
file_path = "zotero.sqlite"

#Define global vars
cursor: SQLiteDatabase
connection: SQLiteDatabase

itemMap: dict[int, ItemObj] = {}
annotation_map: dict[Tuple[int, int], AnnotationObj] = {}
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

def get_annotations():
    """:returns MAP of annotations and tags within these annotations
    :type Annotations are individual items that have their own itemID, but they also have a parent id
    The parent id relates the item to a central node or 'item'.
    1-Many relationship"""
    global noIdCount
    tag_query = ("SELECT itemAnnotations.itemID, itemAnnotations.parentItemID,"
             "itemAnnotations.text, itemAnnotations.comment, itemAnnotations.color "
             "FROM itemAnnotations")
    cursor_execute = cursor.execute(tag_query)
    annotation_list = cursor_execute.fetchall()
    for annotation_item in annotation_list:
        try:
            #Needs to be tagID
            parent_key: int = annotation_item[2]
            tag_id: int = annotation_item[0]

            annotation_map[(parent_key, tag_id)] = AnnotationObj(parent_key, annotation_item[0], annotation_item[6], annotation_item[5], annotation_item[4], annotation_item[1])
        except (RuntimeError, TypeError, NameError):
            # If for whatever reason there isn't a parent key
            parent_key = noIdCount
            annotation_map[parent_key] = AnnotationObj(annotation_item[2], annotation_item[0], annotation_item[6], annotation_item[5], annotation_item[4], annotation_item[1])
            noIdCount = + 1
    return annotation_map

def get_tags():
    """:returns map of tags, their names, types, and relevant ID's: Dict[TagID:[ItemID, type, name]]
    Many-Many Relationship in relation to item entities"""
    query = ("SELECT itemTags.tagID, itemTags.itemID, itemTags.type, tags.name "
             "FROM itemTags INNER JOIN tags ON tags.tagID = itemTags.tagID ")
    cursor_execute = cursor.execute(query)
    return cursor_execute.fetchall()


def get_items():
    """:returns map of individual items."""
    item_query = (
        # Parent collection id is not needed for items, because that logic will be covered in
        # obtaining the actual collections in get_collections function
        "SELECT collectionItems.collectionID, collectionItems.itemID, collections.collectionName"
        " FROM collections FULL JOIN collectionItems ON collections.collectionID = collectionItems.collectionID")
    cursor_execute = (cursor.execute(item_query))
    #print([i[0] for i in cursor.description])
    item_list = cursor_execute.fetchall()
    for item_obj in item_list:
        itemMap[item_obj[1]] = item_obj[1]
        #itemMap[parent_item[0]] = ItemObj(parent_item[0], parent_item[3], parent_item[2], {})
    return itemMap

def get_collections(library: BaseLibrary):
    """:returns a list of all collections
    library ID can be range from 1 to n, depending on how what library the user wants to draw from (most users will have 1)
    Future update should allow to combine all libraries using relational algebra or smth
    """
    collection_query = ("SELECT collections.collectionID, collections.collectionName, collections.parentCollectionID "
        " FROM collections WHERE collections.libraryID == ?")
    cursor_execute = (cursor.execute(collection_query, (library.library_id,)))
    collection_list = cursor_execute.fetchall()
    library.add_collection(collection_list, library)
    return library.collectionMap

def main():
    # Define Vars
    library: BaseLibrary


    connect()
    library = instantiate_library()
    get_collections(library)
    get_annotations()
    get_items()

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