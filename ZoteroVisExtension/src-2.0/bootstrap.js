(() => {
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __esm = (fn, res) => function __init() {
    return fn && (res = (0, fn[__getOwnPropNames(fn)[0]])(fn = 0)), res;
  };
  var __commonJS = (cb, mod) => function __require() {
    return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
  };

  // api-override.ts
  async function getDataRequest(sqlQuery, keyList, libraryID) {
    try {
      let rows = typeof libraryID !== void 0 ? await Zotero.DB.queryAsync(sqlQuery, libraryID) : await Zotero.DB.queryAsync(sqlQuery);
      return [200, "application/json", JSON.stringify(rows.map((row) => {
        const entries = keyList.map((key) => [key, row[key]]);
        return Object.fromEntries(entries);
      }))];
    } catch (e) {
      Zotero.debug(`Data Request Error: ${e.message}`);
      throw e;
    }
  }
  var ApiOverride, dataRequest;
  var init_api_override = __esm({
    "api-override.ts"() {
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
          Zotero.Server.Endpoints["/api/tags"] = this.tagEndpoint;
          Zotero.Server.Endpoints["/api/collectionItem"] = this.collectionItemEndpoint;
          Zotero.Server.Endpoints["/api/annotationItem"] = this.annotationsEndpoint;
        },
        tagEndpoint: function() {
        },
        collectionItemEndpoint: function() {
        },
        annotationsEndpoint: function() {
        },
        allItemsEndpoint: function() {
        },
        fieldItems: function() {
        },
        getDataRequest: function() {
        },
        collections: function() {
        },
        selfDestruct() {
          ApiOverride = null;
        }
      };
      dataRequest = {
        init: async function(options) {
          Zotero.debug(options.pathname);
          Zotero.debug(" Collection Endpoint method Called");
          try {
            switch (options.pathname) {
              case "/api/tags":
                return await getDataRequest(`SELECT itemTags.tagID, itemTags.itemID, itemTags.type, tags.name FROM itemTags 
                        INNER JOIN tags ON tags.tagID = itemTags.tagID ORDER BY itemTags.itemID ASC`, ["tagID", "itemID", "type", "name"]);
              case "/api/annotationItem":
                return await getDataRequest(
                  `SELECT itemAnnotations.itemID, itemAnnotations.parentItemID, 
                        itemAnnotations.text, itemAnnotations.comment, itemAnnotations.color, 
                        items.itemTypeID, items.dateAdded, items.clientDateModified 
                        FROM itemAnnotations INNER JOIN items ON itemAnnotations.itemID == items.itemID 
                        ORDER BY itemAnnotations.parentItemID ASC`,
                  ["itemID", "parentItemID", "text", "comment", "color", "itemTypeID", "dateAdded", "clientDateModified"]
                );
              case "/api/collectionItem":
                return await getDataRequest(`SELECT collectionItems.collectionID, items.itemID, collections.collectionName, items.itemTypeID, items.dateAdded, 
                        items.clientDateModified, itemAttachments.parentItemID, itemAttachments.linkMode, itemAttachments.path, itemAttachments.contentType 
                        FROM items FULL JOIN collectionItems ON collectionItems.itemID = items.itemID 
                        FULL JOIN itemAttachments ON itemAttachments.itemID = items.itemID 
                        FULL JOIN collections ON collectionItems.collectionID = collections.collectionID 
                        WHERE ((items.libraryID == ?) AND (items.itemTypeID NOT IN (1, 28))) ORDER BY items.itemId ASC`, ["collectionID", "itemID", "collectionName", "itemTypeID", "dateAdded", "clientDateModified", "parentItemID", "linkMode", "path", "contentType"], 1);
              default:
                return [404, "application/json", JSON.stringify({ error: "Path not found" })];
            }
          } catch (e) {
            return [500, "text/plain", `Error: ${e.message}`];
          }
        }
      };
      ApiOverride.tagEndpoint.prototype = dataRequest;
      ApiOverride.collectionItemEndpoint.prototype = dataRequest;
      ApiOverride.annotationsEndpoint.prototype = dataRequest;
    }
  });

  // bootstrap.ts
  var require_bootstrap = __commonJS({
    "bootstrap.ts"() {
      init_api_override();
      function log(msg) {
        Zotero.debug("Zotero Knowledge Vis " + msg);
      }
      function install() {
        log("Installed 2.0");
      }
      async function startup({ id, version, rootURI }) {
        log("Starting 2.0");
        Zotero.PreferencePanes.register({
          pluginID: "zotero-knowledge-vis@example.com",
          src: rootURI + "preferences.xhtml",
          scripts: [rootURI + "preferences.js"]
        });
        ApiOverride.init({ id, version, rootURI });
      }
      function shutdown() {
        log("Shutting down 2.0");
        ApiOverride.selfDestruct();
      }
      function uninstall() {
        log("Uninstalled 2.0");
      }
      globalThis.startup = startup;
      globalThis.shutdown = shutdown;
      globalThis.install = install;
      globalThis.uninstall = uninstall;
    }
  });
  require_bootstrap();
})();
