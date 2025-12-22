import sqlite3
import logging
from sqlite3 import OperationalError

from pandas.io.sql import SQLiteDatabase

from src.models import CollectionObj, ItemObj, TagObj
logger = logging.getLogger(__name__)
file_path = "zotero.sqlite"


# Initial connection, for now it's directory, but ideally we want users to be able to make a copy of this.... just in case


# global vars
itemTagList: list[object] = []

#def findRelationship(self):
 #   self.TagObj1


collectionMap: dict[int, CollectionObj] = {}
itemMap: dict[int, ItemObj] = {}
annotation_map: dict[int, TagObj] = {}
relationshipList = []
noIdCount: int = 0
cursor: SQLiteDatabase
connection: SQLiteDatabase


def get_annotations():
    """:returns MAP of annotations and tags within these annotations
    :type Annotations are individual items that have their own itemID, but they also have a parent id
    The parent id relates the item to a central node or 'item'.
    Many-Many relationship"""
    global noIdCount
    tag_query = ("SELECT tags.tagID, tags.name, itemTags.itemID, itemTags.type, itemAnnotations.parentItemID,"
             "itemAnnotations.text, itemAnnotations.comment, itemAnnotations.color "
             "FROM tags FULL JOIN itemTags ON tags.tagID = itemTags.tagID INNER JOIN itemAnnotations ON itemAnnotations.itemID = itemTags.itemID ")
    cursor_execute = cursor.execute(tag_query)
    #print([i[0] for i in cursor.description])
    annotation_list = cursor_execute.fetchall()
    for annotation_item in annotation_list:
        try:
            parent_key: int = annotation_item[2]
            annotation_map[parent_key] = TagObj(annotation_item[2], annotation_item[0], annotation_item[6], annotation_item[5], annotation_item[4], annotation_item[1])
        except (RuntimeError, TypeError, NameError):
            # If for whatever reason there isn't a parent key
            parent_key = noIdCount
            annotation_map[parent_key] = TagObj(annotation_item[2], annotation_item[0], annotation_item[6], annotation_item[5], annotation_item[4], annotation_item[1])
            noIdCount = + 1
    return annotation_map

def get_items():
    """:returns map of individual items.
    """
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

def get_collections():
    """:returns a list of all collections"""
    collection_query = ("SELECT collections.collectionID, collections.collectionName, collections.parentCollectionID "
        " FROM collections")
    cursor_execute = (cursor.execute(collection_query))
   # print([i[0] for i in cursor.description])
    return cursor_execute.fetchall()

def main():
    global connection
    global cursor
    try:
        connection = sqlite3.connect(f"file:{file_path}?mode=rw", uri=True)
        cursor = connection.cursor()
        print(cursor.execute("SELECT 1").fetchall())
    except Exception as e:
        print(f"Database Connection failed: {e}. Check to see if the zotero.sqlite file is located in the root directory, and it is spelled exactly as <zotero.sqlite>, or whatever value you have in file_path")
        raise Exception
    get_annotations()
    itemList = get_items()
    collectionList = get_collections()
    get_items()

    """
    If parentCollectionID === None
        parentCollectionID = 'main'
    """

    for item in annotation_map.values():
        print(item)

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