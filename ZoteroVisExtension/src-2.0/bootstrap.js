var testVar;
var ApiOverride;

function log(msg) {
	Zotero.debug("Make It Red: " + msg);
}

function install() {
	log("Installed 2.0");
}

async function startup({ id, version, rootURI }) {
	log("Starting 2.0");
    Services.scriptloader.loadSubScript(rootURI + 'api-override.ts');
    ApiOverride.init({ id, version, rootURI})
    let results = await ApiOverride.getTags();
    log(results)
}

function shutdown() {
	log("Shutting down 2.0");
	ApiOverride = undefined;
}

function uninstall() {
	log("Uninstalled 2.0");
}
