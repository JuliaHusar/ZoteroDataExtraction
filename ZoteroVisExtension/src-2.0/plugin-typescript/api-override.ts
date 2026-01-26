
export let ApiOverride:ApiOverride = {
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

        Zotero.Server.Endpoints["/myAddon/tags"] = this.tagEndpoint
        Zotero.Server.Endpoints["/myAddon/collectionItem"] = this.collectionItemEndpoint
        Zotero.Server.Endpoints["/myAddon/annotationItem"] = this.annotationsEndpoint

    },
    tagEndpoint: function() {},
    collectionItemEndpoint: function() {},
    annotationsEndpoint: function() {},
    allItemsEndpoint: function() {},
    fieldItems: function() {},
    getDataRequest: function() {},
    collections: function() {},
    selfDestruct(){
        ApiOverride = null
    }
};

const dataRequest = {
    init: async function(options) {
        Zotero.debug(options.pathname)
        Zotero.debug(" Collection Endpoint method Called")
        try {
            switch (options.pathname){
                case "/myAddon/tags":
                    return await getDataRequest(`SELECT itemTags.tagID, itemTags.itemID, itemTags.type, tags.name FROM itemTags 
                        INNER JOIN tags ON tags.tagID = itemTags.tagID ORDER BY itemTags.itemID ASC`, ["tagID", "itemID", "type", "name"]);
                case "/myAddon/annotationItem":
                    return await getDataRequest(`SELECT itemAnnotations.itemID, itemAnnotations.parentItemID, 
                        itemAnnotations.text, itemAnnotations.comment, itemAnnotations.color, 
                        items.itemTypeID, items.dateAdded, items.clientDateModified 
                        FROM itemAnnotations INNER JOIN items ON itemAnnotations.itemID == items.itemID 
                        ORDER BY itemAnnotations.parentItemID ASC`,
                        ["itemID", "parentItemID", "text", "comment", "color", "itemTypeID", "dateAdded", "clientDateModified"]);
                case "/myAddon/collectionItem":
                    return await getDataRequest(`SELECT collectionItems.collectionID, items.itemID, collections.collectionName, items.itemTypeID, items.dateAdded, 
                        items.clientDateModified, itemAttachments.parentItemID, itemAttachments.linkMode, itemAttachments.path, itemAttachments.contentType 
                        FROM items FULL JOIN collectionItems ON collectionItems.itemID = items.itemID 
                        FULL JOIN itemAttachments ON itemAttachments.itemID = items.itemID 
                        FULL JOIN collections ON collectionItems.collectionID = collections.collectionID 
                        WHERE ((items.libraryID == ?) AND (items.itemTypeID NOT IN (1, 28))) ORDER BY items.itemId ASC`,["collectionID", "itemID", "collectionName", "itemTypeID", "dateAdded", "clientDateModified", "parentItemID", "linkMode", "path", "contentType"], 1)
                default:
                    return [404, "application/json", JSON.stringify({error: "Path not found"})]
            }
        } catch (e) {
            return[500, "text/plain", `Error: ${e.message}`];
        }
    }

}
ApiOverride.tagEndpoint.prototype = dataRequest;
ApiOverride.collectionItemEndpoint.prototype = dataRequest;
ApiOverride.annotationsEndpoint.prototype = dataRequest;

async function getDataRequest(sqlQuery: string, keyList: string[], libraryID?: number){
    try {
        let rows: _ZoteroTypes.anyObj[] = typeof libraryID !== undefined ? await Zotero.DB.queryAsync(sqlQuery, libraryID): await Zotero.DB.queryAsync(sqlQuery)
        return[200, "application/json", JSON.stringify(rows.map(row => {
            const entries = keyList.map(key => [key, row[key]]);
            return Object.fromEntries(entries)
        }))];
    } catch (e) {
        Zotero.debug(`Data Request Error: ${e.message}`);
        throw e;
    }
}


interface ApiOverride {
    id: string,
    version: string,
    rootURI: string,
    initialized: boolean,
    addedElementIDs: [],
    tagEndpoint(): void,
    collectionItemEndpoint(): void,
    annotationsEndpoint(): void,
    allItemsEndpoint(): void,
    fieldItems(): void,
    getDataRequest(arg0: string): void,
    collections(): void,
    selfDestruct(): void

    init({id, version, rootURI}): void
}
