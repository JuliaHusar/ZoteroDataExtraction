import {ApiOverride} from "./types";
let ApiOverride: ApiOverride;
ApiOverride = {
    id: null,
    version: null,
    rootURI: null,
    initialized: false,
    addedElementIDs: [],

    init({ id, version, rootURI }) {
        if (this.initialized) return;
        this.id = id;
        this.version = version;
        this.rootURI = rootURI;
        this.initialized = true;
    },
}

export async function getTags(): Promise<object> {
    const sql = `SELECT itemTags.tagID, itemTags.itemID, itemTags.type, tags.name 
                                FROM itemTags INNER JOIN tags ON tags.tagID = itemTags.tagID ORDER BY itemTags.itemID ASC`
    let rows = await Zotero.DB.queryAsync(sql);
    let cleanData = rows.map(row => {
        return {
            name: row.name,
            type: row.type,
            tag_id: row.tagID
        };
    });

    return cleanData
}
export async function getCollectionItems(libraryNumber: number): Promise<any> {
        const sql = `SELECT collectionItems.collectionID, items.itemID, collections.collectionName, items.itemTypeID, items.dateAdded, 
       items.clientDateModified, itemAttachments.parentItemID, itemAttachments.linkMode, itemAttachments.path, itemAttachments.contentType 
        FROM items FULL JOIN collectionItems ON collectionItems.itemID = items.itemID 
        FULL JOIN itemAttachments ON itemAttachments.itemID = items.itemID 
        FULL JOIN collections ON collectionItems.collectionID = collections.collectionID 
        WHERE ((items.libraryID == ?) AND (items.itemTypeID NOT IN (1, 28))) ORDER BY items.itemId ASC`
        try {
            return await Zotero.DB.queryAsync(sql, libraryNumber);
        } catch (e) {
            Zotero.debug(`MyAddon Error: ${e.message}`);
            throw e;
        }
}
