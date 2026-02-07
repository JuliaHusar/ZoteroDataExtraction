import {ApiOverride} from "./api-override";

function log(msg) {
	Zotero.debug("Zotero Knowledge Vis " + msg);
}

function install() {
	log("Installed 2.0");
}

async function startup({ id, version, rootURI }) {
	log("Starting 2.0");
    Zotero.PreferencePanes.register({
        pluginID: 'zotero-knowledge-vis@example.com',
        src: rootURI + 'preferences.xhtml',
        scripts: [rootURI + 'preferences.js']
    });
    ApiOverride.init({ id, version, rootURI})
   // log(tagEndpointResult)
   // let results = getCollectionItems()
}

function onMainWindowLoad({ window }) {
}

function onMainWindowUnload({ window }) {
}

function shutdown() {
	log("Shutting down 2.0");
    ApiOverride.selfDestruct()
}

function uninstall() {
	log("Uninstalled 2.0");
}

(globalThis as any).startup = startup;
(globalThis as any).shutdown = shutdown;
(globalThis as any).install = install;
(globalThis as any).uninstall = uninstall;