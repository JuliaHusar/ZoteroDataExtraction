import sqlite3
import numpy as np
import pandas as pd


# Initial connection, for now it's directory, but ideally we want users to be able to make a copy of this.... just in case
connection = sqlite3.connect("zotero.sqlite")
cursor = connection.cursor()

# global vars

class TagObj:
    def __init__(self, item_id, tag_id, comment, text, parent_item_id, name):
        self.item_id  = item_id
        self.tag_id = tag_id
        self.comment = comment
        self.text = text
        self.parent_item_id = parent_item_id
        self.name = name
    def __str__(self):
        return f"{self.item_id} {self.tag_id} {self.comment}"


tagObjList = []


def get_tags():
    query = ("SELECT tags.tagID, tags.name, itemTags.itemID, itemAnnotations.parentItemID, itemAnnotations.text, itemAnnotations.comment, itemAnnotations.color, itemAnnotations.position "
             "FROM tags INNER JOIN itemTags ON tags.tagID = itemTags.tagID FULL OUTER JOIN itemAnnotations ON itemAnnotations.itemID = itemTags.itemID ")
    cursorExecute = (cursor.execute(query))
    print( [i[0] for i in cursor.description])
    return cursorExecute.fetchall()

sqlList = get_tags()

for item in sqlList:
     tagObjList.append(TagObj(item[2], item[0], item[5], item[4], item[3], item[1]))

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